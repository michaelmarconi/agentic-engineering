#!/usr/bin/env python3
"""Hand the correction checker the review report and the document as reviewed, word for word.

After a review, the drafting agent corrects the document once and starts the correction checker
(see docs/adrs/0010 and 0011). The checker needs two texts it cannot see: the reviewer's report,
and the document as it stood when reviewed. A model copying them can reword them, so this hook
saves them and adds them to the checker's request itself.

Claude Code runs it on PreToolUse and PostToolUse for the Agent tool, and on SessionEnd. It reads
the hook's JSON from stdin. A reviewer's or checker's request must start with the line
`Document: <path>`. Skills give the document's full path; a relative path is read from a
`Repository: <folder>` second line if the request has one, or else from the project
($CLAUDE_PROJECT_DIR, or the current directory if unset). It may name several files separated by
commas, such as `Document: /p/AGENTS.md, /p/docs/practices/testing.md`, which are then reviewed as
one document (see docs/adrs/0018): the hook saves each, hands the checker each between `=== FILE: <path> ===` and
`=== END FILE ===` lines, and starts the checker once any of them has changed. The order of the
names does not matter, and a line naming one existing file is that file even if its name holds a
comma. A draft that is never written to a file, such as /feedback's,
uses `Document: feedback draft` and carries the draft between `=== DRAFT ===` and
`=== END DRAFT ===` lines in the request.

Before any of these agents starts, the hook finds the repository the document is in (see
docs/adrs/0022): the top folder of the git repository holding its files, or the project when they
are in none. It rewrites the request's first line to name each file relative to that folder, and
puts `Repository: <the folder's full path>` on the second line, so an agent started from a folder
above the project still reads and searches the right one. Everything it saves is keyed by those
relative paths. It refuses the start when none of the files exists, or when they sit in different
repositories. A feedback draft has no file, so its requests are left as they are.

Every review has two parts that run side by side: the skill's own reviewer (spec, brief, adr, plan,
feedback, practices or spike) and the shared language checker, which checks the wording (see docs/adrs/0013).

- Before either starts, it saves the document's text. A part joins the latest review of that
  document if it is of the same text apart from spacing and has no report from this part yet, so
  a part started again after a run that never reported still joins it; otherwise it begins a new
  review. The text kept is the copy the reviewer saw. A few recent reviews are kept, and always
  the newest the reviewer ran in, so a part run again on its own never wipes the review it
  follows.
- When either finishes, it saves that part's report in the review its run started in. In a
  Claude project thread the report is the one the agent handed back, not the tool's text, which
  there only says where the report went. Claude Code gives both events of one run the same `tool_use_id`; without one, the agent's name
  stands in for it.
- Either part started in the background is refused, when reviews are being saved: its report
  would arrive after the hook has already seen the run finish.
- Before the correction checker starts, it takes the latest review the reviewer ran in, appends
  both its reports, the document as reviewed, and the files that skill's checker should read,
  between fixed `=== ... ===` lines, and approves the start. It refuses the start, with a reason
  Claude sees, when the request has no `Document:` line, when that review lacks either report or
  none is on record in this session, or when the document is unchanged since its review. No
  refusal asks for another review, which the lifecycle never repeats: when a report is missing,
  it tells Claude to stop and show the person.
- When the checker finishes, it deletes that document's saved review, so a later review of the
  same document, such as a spike record's verdict review after its design review, starts a new
  cycle; at the end of the session
  it deletes all of the session's.

Saved reviews live in $CLAUDE_PLUGIN_DATA/reviews/<session>/, outside the project, one file per
document. Without $CLAUDE_PLUGIN_DATA nothing is saved. Any other agent or tool, and any input it
cannot read, is left alone, so the hook never blocks anything else.
"""

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

try:
    import fcntl
except ImportError:  # Windows: run without the lock rather than fail every agent start.
    fcntl = None

ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FEEDBACK_DRAFT = "feedback draft"
DRAFT_START = "=== DRAFT ===\n"
DRAFT_END = "=== END DRAFT ==="
REPOSITORY = "Repository:"
CHECKER = "correction-checker"
LANGUAGE = "language-checker"
LIFECYCLE = os.path.join(ROOT, "docs", "lifecycle.md")
KEPT = 3  # reviews kept per document
# Each reviewer's skill, and the project files its checker may read to judge a changed sentence.
REVIEWERS = {
    "spec-reviewer": ("spec", ["docs/brief.md", "docs/specs/", "docs/adrs/", "docs/plans/", "docs/spikes/"]),
    "brief-reviewer": ("brief", ["docs/specs/", "docs/adrs/", "docs/plans/", "docs/spikes/"]),
    "adr-reviewer": ("adr", ["docs/adrs/", "docs/spikes/"]),
    "feedback-reviewer": ("feedback", []),
    "plan-reviewer": ("plan", ["docs/specs/", "docs/adrs/", "docs/plans/", "docs/spikes/"]),
    "spike-reviewer": ("spike", ["docs/specs/", "docs/adrs/"]),
    "practices-reviewer": ("practices", ["docs/practices/", "docs/adrs/", "CLAUDE.md",
                                         "the repository's build, dependency, CI and setup files"]),
}


def agent_name(tool_input):
    name = tool_input.get("subagent_type")
    return name.split(":")[-1] if isinstance(name, str) else None


def document(prompt):
    """Return the document named on the request's first line, or None."""
    lines = prompt.strip().splitlines() if isinstance(prompt, str) else []
    if not lines or not lines[0].startswith("Document:"):
        return None
    return lines[0][len("Document:"):].strip() or None


def draft(prompt):
    start = prompt.find(DRAFT_START)
    end = prompt.find(DRAFT_END, start + len(DRAFT_START)) if start >= 0 else -1
    return prompt[start + len(DRAFT_START):end] if end >= 0 else None


def project():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


class Unreadable(Exception):
    """The `Document:` line names no file the hook can find, or files in different repositories."""


def repository_line(prompt):
    """The folder on the request's second line, `Repository: <folder>`, or None."""
    lines = prompt.strip().splitlines()
    if len(lines) > 1 and lines[1].startswith(REPOSITORY):
        return lines[1][len(REPOSITORY):].strip() or None
    return None


def git_top(path):
    """The top folder of the git repository holding `path`, or None when it is in none."""
    folder = os.path.dirname(path)
    while True:
        if os.path.exists(os.path.join(folder, ".git")):
            return folder
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def locate(name, prompt):
    """The document's repository and its files relative to it, sorted (ADR 0018 and 0022).

    A line that names an existing file is that one file, even if its name holds a comma, so the
    order of the names on the line never matters. Raises Unreadable when no named file exists, or
    when they sit in different repositories."""
    if name == FEEDBACK_DRAFT:
        return None, [FEEDBACK_DRAFT]
    base = repository_line(prompt) or project()

    def full(path):
        return os.path.realpath(path if os.path.isabs(path) else os.path.join(base, path))

    parts = [name]
    if "," in name and not os.path.isfile(full(name)):
        parts = [p.strip() for p in name.split(",") if p.strip()]
    paths = [full(p) for p in parts]
    found = [p for p in paths if os.path.isfile(p)]
    if not found:
        raise Unreadable(f"Can't find {name}. Give the document's full path on the `Document:` "
                         "line, the path you wrote it to, and start the agent again.")
    tops = sorted({git_top(p) or os.path.realpath(project()) for p in found})
    if len(tops) > 1:
        raise Unreadable(f"The files on the `Document:` line, {name}, sit in different "
                         f"repositories: {', '.join(tops)}. Name only one repository's files.")
    return tops[0], sorted({os.path.relpath(p, tops[0]) for p in paths})


def rewritten(tool_input, repository, paths):
    """The request with `Document:` naming the files relative to the repository and
    `Repository:` on the second line, in place of any the request had."""
    lines = (tool_input.get("prompt") or "").strip("\n").splitlines()
    rest = lines[1:]
    if rest and rest[0].startswith(REPOSITORY):
        rest = rest[1:]
    prompt = "\n".join([f"Document: {', '.join(paths)}", f"{REPOSITORY} {repository}", *rest])
    return dict(tool_input, prompt=prompt)


def allow(updated):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow",
                                   "updatedInput": updated}}


def read(repository, path):
    try:
        with open(os.path.join(repository, path), encoding="utf-8") as f:
            return f.read()
    except (OSError, ValueError):
        return None


def current_text(repository, paths, prompt):
    """The document's text now: the draft in the request, or the files' contents.

    Several files are joined, each between `=== FILE: <path> ===` and `=== END FILE ===`
    lines, with a file that does not exist shown as `(missing)`; when none exists there is no
    text."""
    if paths == [FEEDBACK_DRAFT]:
        return draft(prompt)
    if len(paths) == 1:
        return read(repository, paths[0])
    texts = [read(repository, p) for p in paths]
    if all(t is None for t in texts):
        return None
    return "".join(f"=== FILE: {p} ===\n" + ("(missing)" if t is None else t) + "\n=== END FILE ===\n"
                   for p, t in zip(paths, texts))


def folder(session):
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not data:
        return None
    safe = session if re.fullmatch(r"[A-Za-z0-9_-]{1,100}", session) else hashlib.sha256(
        session.encode()).hexdigest()
    return os.path.join(data, "reviews", safe)


def record_path(session, name):
    base = folder(session)
    return os.path.join(base, hashlib.sha256(name.encode()).hexdigest() + ".json") if base else None


@contextlib.contextmanager
def locked(session, create=True):
    """Hold the session's lock: both parts of a review can finish at the same moment.

    Untested, since only a race could show it and no test relies on timing (AGENTS.md rule 5)."""
    base = folder(session)
    if not base or not fcntl or not (create or os.path.isdir(base)):
        yield
        return
    os.makedirs(base, exist_ok=True)
    handle = os.open(base, os.O_RDONLY)
    try:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield
    finally:
        os.close(handle)


def valid(review):
    if not (isinstance(review, dict) and isinstance(review.get("text"), str)
            and isinstance(review.get("reports"), dict) and isinstance(review.get("started"), dict)):
        return False
    return all(isinstance(v, str) for v in review["reports"].values())


def load(session, name):
    """The document's saved reviews, oldest first; any not in this version's shape are dropped."""
    path = record_path(session, name)
    try:
        with open(path, encoding="utf-8") as f:
            saved = json.load(f)
    except (OSError, TypeError, ValueError):
        return []
    reviews = saved.get("reviews") if isinstance(saved, dict) else None
    return [r for r in reviews if valid(r)] if isinstance(reviews, list) else []


def reviewed(review):
    return "reviewer" in review["started"].values()


def trim(reviews):
    """The last few reviews, and the newest the reviewer ran in even when it is older than those."""
    kept = reviews[-KEPT:]
    if not any(reviewed(r) for r in kept):
        kept = [r for r in reviews if reviewed(r)][-1:] + kept
    return kept


def save(session, name, reviews):
    path = record_path(session, name)
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    handle, temp = tempfile.mkstemp(dir=os.path.dirname(path))
    with os.fdopen(handle, "w", encoding="utf-8") as f:
        json.dump({"reviews": trim(reviews)}, f)
    os.replace(temp, path)


def forget(session, name):
    try:
        os.remove(record_path(session, name))
    except (OSError, TypeError):
        pass


def response_text(response):
    """The agent's report. In a Claude project thread the subagent hands it back through its
    SubagentHandback tool: it is then in `handbackReport`, and `content` only says where it went."""
    if isinstance(response, dict):
        if "handback" in response or "handbackReport" in response:
            report = response.get("handbackReport")
            text = report.get("text") if isinstance(report, dict) else None
            return text if isinstance(text, str) else ""
        blocks = response.get("content") or []
        return "".join(b.get("text") or "" for b in blocks if isinstance(b, dict))
    return response if isinstance(response, str) else ""


def refuse(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def reviewer_of(review):
    return next((k for k in review["reports"] if k in REVIEWERS), None)


def complete(review):
    return reviewer_of(review) is not None and LANGUAGE in review["reports"]


def has_report(review, part):
    return LANGUAGE in review["reports"] if part == "language" else reviewer_of(review) is not None


def same_text(a, b):
    return " ".join(a.split()) == " ".join(b.split())


def attachments(name, record):
    reviewer = reviewer_of(record)
    skill, extra = REVIEWERS[reviewer]
    lines = [f"Rubric: {os.path.join(ROOT, 'skills', skill, 'references', 'rubric.md')}",
             f"Plain words rule: the Plain words section of {LIFECYCLE}"]
    if extra:
        lines.append("Only where needed to judge a changed sentence: " + ", ".join(extra))
    reports = record["reports"]
    return ("\n\n=== REVIEW REPORT ===\n" + reports[reviewer] + "\n=== END REVIEW REPORT ===\n\n"
            "=== WORDING REPORT ===\n" + reports[LANGUAGE] + "\n=== END WORDING REPORT ===\n\n"
            f"=== DOCUMENT AS REVIEWED: {name} ===\n" + record["text"] + "\n=== END DOCUMENT ===\n\n"
            "=== FILES TO READ ===\n" + "\n".join(lines) + "\n=== END FILES TO READ ===\n")


def start_checker(session, tool_input):
    prompt = tool_input.get("prompt") or ""
    named = document(prompt)
    if not named:
        return refuse("Start the correction checker with `Document: <path>` as the first line of "
                      "its request, the same line the reviewer was given.")
    try:
        repository, paths = locate(named, prompt)
    except Unreadable as problem:
        return refuse(str(problem))
    name = ", ".join(paths)
    with locked(session, create=False):
        reviews = [r for r in load(session, name) if reviewed(r)][-1:]
    if not reviews or not complete(reviews[0]):
        return refuse(f"No review of {name} with both the reviewer's and the language checker's "
                      "reports is on record in this session, so the corrections cannot be "
                      "checked. Do not review again: stop and show the person the reports you "
                      "have and this reason.")
    record = reviews[-1]
    text = current_text(repository, paths, prompt)
    if text == record["text"]:
        return refuse(f"{name} is unchanged since its review. Make the corrections first, then "
                      "start the correction checker.")
    updated = rewritten(tool_input, repository, paths) if repository else dict(tool_input)
    updated["prompt"] += attachments(name, record)
    return allow(updated)


def handle(event):
    """Return the hook's JSON output, or None to leave the step alone."""
    if not isinstance(event, dict):
        return None
    session = str(event.get("session_id") or "unknown")
    when = event.get("hook_event_name")
    if when == "SessionEnd":
        base = folder(session)
        if base:
            shutil.rmtree(base, ignore_errors=True)
        return None
    tool_input = event.get("tool_input")
    if event.get("tool_name") not in ("Agent", "Task") or not isinstance(tool_input, dict):
        return None
    agent = agent_name(tool_input)
    prompt = tool_input.get("prompt") or ""
    named = document(prompt)
    if agent == CHECKER:
        if when == "PreToolUse":
            return start_checker(session, tool_input)
        if when == "PostToolUse" and named:
            try:
                name = ", ".join(locate(named, prompt)[1])
            except Unreadable:
                return None
            with locked(session, create=False):
                forget(session, name)
        return None
    if (agent not in REVIEWERS and agent != LANGUAGE) or not named:
        return None
    if when == "PreToolUse" and tool_input.get("run_in_background") and folder(session):
        return refuse("Start the reviewer and the language checker in the foreground, not in the "
                      "background, so their reports are kept for the correction check.")
    try:
        repository, paths = locate(named, prompt)
    except Unreadable as problem:
        return refuse(str(problem)) if when == "PreToolUse" else None
    name = ", ".join(paths)
    call = str(event.get("tool_use_id") or agent)
    part = "reviewer" if agent in REVIEWERS else "language"
    start = allow(rewritten(tool_input, repository, paths)) if repository else None
    if when == "PreToolUse" and not folder(session):
        return start
    with locked(session):
        reviews = load(session, name)
        if when == "PreToolUse":
            text = current_text(repository, paths, prompt)
            if text is None:
                return start
            latest = reviews[-1] if reviews else None
            if not (latest and same_text(latest["text"], text) and not has_report(latest, part)):
                latest = {"text": text, "reports": {}, "started": {}}
                reviews.append(latest)
            if part == "reviewer":
                latest["text"] = text  # the copy the reviewer saw is the one kept
            latest["started"][call] = part
            save(session, name, reviews)
            return start
        elif when == "PostToolUse":
            report = response_text(event.get("tool_response"))
            for review in reversed(reviews):
                if call in review["started"]:
                    if report.strip():
                        review["reports"][agent] = report
                        save(session, name, reviews)
                    break
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Reads one Claude Code hook event as JSON from stdin. Prints a PreToolUse decision "
               "as JSON when it starts or refuses the correction checker, and nothing otherwise. "
               "Always exits 0. Saved reviews go under $CLAUDE_PLUGIN_DATA/reviews/.")
    parser.parse_args(argv)
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    try:
        out = handle(event)
    except Exception:  # never block a step over a fault in this hook
        out = None
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
