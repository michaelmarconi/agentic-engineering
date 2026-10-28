#!/usr/bin/env python3
"""Hand the correction checker the review report and the document as reviewed, word for word.

After a review, the drafting agent corrects the document once and starts the correction checker
(see docs/adrs/0010 and 0011). The checker needs two texts it cannot see: the reviewer's report,
and the document as it stood when reviewed. A model copying them can reword them, so this hook
saves them and adds them to the checker's request itself.

Claude Code runs it on PreToolUse and PostToolUse for the Agent tool, and on SessionEnd. It reads
the hook's JSON from stdin. A reviewer's or checker's request must start with the line
`Document: <path>`, a path relative to the project ($CLAUDE_PROJECT_DIR, or the current
directory if unset) or absolute. A draft that is never written to a file, such as /issue's,
uses `Document: issue draft` and carries the draft between `=== DRAFT ===` and
`=== END DRAFT ===` lines in the request.

Every review has two parts that run side by side: the skill's own reviewer (spec, brief, adr or
issue) and the shared language checker, which checks the wording (see docs/adrs/0013).

- Before either starts, it saves the document's text. The two parts of one review join one
  record; a part that starts on a different text, or that already reported on this one, begins
  a new review, replacing any earlier review of that document in this session.
- When either finishes, it saves that part's report.
- Before the correction checker starts, it appends both reports, the document as reviewed, and
  the files that skill's checker should read, between fixed `=== ... ===` lines, and approves
  the start. It refuses the start, with a reason Claude sees, when the request has no
  `Document:` line, when either report of that document is not on record in this session, or
  when the document is unchanged since its review.
- When the checker finishes, it deletes that document's saved review; at the end of the session
  it deletes all of the session's.

Saved reviews live in $CLAUDE_PLUGIN_DATA/reviews/<session>/, outside the project, one file per
document. Without $CLAUDE_PLUGIN_DATA nothing is saved. Any other agent or tool, and any input it
cannot read, is left alone, so the hook never blocks anything else.
"""

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ISSUE = "issue draft"
DRAFT_START = "=== DRAFT ===\n"
DRAFT_END = "=== END DRAFT ==="
CHECKER = "correction-checker"
LANGUAGE = "language-checker"
LIFECYCLE = os.path.join(ROOT, "docs", "lifecycle.md")
# Each reviewer's skill, and the project files its checker may read to judge a changed sentence.
REVIEWERS = {
    "spec-reviewer": ("spec", ["docs/brief.md", "docs/specs/"]),
    "brief-reviewer": ("brief", []),
    "adr-reviewer": ("adr", ["docs/adrs/"]),
    "issue-reviewer": ("issue", []),
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


def key(name):
    if name == ISSUE:
        return ISSUE
    full = name if os.path.isabs(name) else os.path.join(project(), name)
    return os.path.relpath(os.path.normpath(full), project())


def current_text(name, prompt):
    """The document's text now: the draft in the request, or the file's contents."""
    if name == ISSUE:
        return draft(prompt)
    try:
        with open(os.path.join(project(), name), encoding="utf-8") as f:
            return f.read()
    except (OSError, ValueError):
        return None


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
def locked(session):
    """Hold the session's lock: both parts of a review can finish at the same moment.

    Untested, since only a race could show it and no test relies on timing (AGENTS.md rule 5)."""
    base = folder(session)
    if not base:
        yield
        return
    os.makedirs(base, exist_ok=True)
    handle = os.open(base, os.O_RDONLY)
    try:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield
    finally:
        os.close(handle)


def load(session, name):
    path = record_path(session, name)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, TypeError, ValueError):
        return None


def save(session, name, record):
    path = record_path(session, name)
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    handle, temp = tempfile.mkstemp(dir=os.path.dirname(path))
    with os.fdopen(handle, "w", encoding="utf-8") as f:
        json.dump(record, f)
    os.replace(temp, path)


def forget(session, name):
    try:
        os.remove(record_path(session, name))
    except (OSError, TypeError):
        pass


def response_text(response):
    if isinstance(response, dict):
        blocks = response.get("content") or []
        return "".join(b.get("text", "") for b in blocks if isinstance(b, dict))
    return response if isinstance(response, str) else ""


def refuse(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def attachments(name, record):
    reviewer = record["reviewer"]
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
    name = key(named)
    record = load(session, name) or {}
    reports = record.get("reports", {})
    if record.get("reviewer") not in reports:
        return refuse(f"No review of {name} is on record in this session, so there is nothing to "
                      "check the corrections against. Run the review first.")
    if LANGUAGE not in reports:
        return refuse(f"The language checker's report on {name} is not on record in this "
                      "session. Start the language checker beside the reviewer, on the same "
                      "document, before correcting.")
    if current_text(name, prompt) == record["text"]:
        return refuse(f"{name} is unchanged since its review. Make the corrections first, then "
                      "start the correction checker.")
    updated = dict(tool_input, prompt=prompt + attachments(name, record))
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow",
                                   "updatedInput": updated}}


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
            forget(session, key(named))
        return None
    if (agent not in REVIEWERS and agent != LANGUAGE) or not named:
        return None
    name = key(named)
    with locked(session):
        record = load(session, name)
        if when == "PreToolUse":
            text = current_text(name, prompt)
            if text is None:
                return None
            if not record or record["text"] != text or agent in record["reports"] or (
                    agent in REVIEWERS and record.get("reviewer") not in (None, agent)):
                record = {"text": text, "reviewer": None, "reports": {}}
            if agent in REVIEWERS:
                record["reviewer"] = agent
            record.setdefault("started", [])
            if agent not in record["started"]:
                record["started"].append(agent)
            save(session, name, record)
        elif when == "PostToolUse":
            report = response_text(event.get("tool_response"))
            if record and agent in record.get("started", []) and report.strip():
                record["reports"][agent] = report
                save(session, name, record)
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
    except OSError:
        out = None
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
