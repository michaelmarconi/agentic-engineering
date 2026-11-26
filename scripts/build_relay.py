#!/usr/bin/env python3
"""Hand the build's correction checker the three review reports and the commit they reviewed.

After its three reviews, /build corrects what they found, once, commits, and starts the
`build-correction-checker` agent. The checker needs the reports word for word, and the commit
the reviews saw, so it can read exactly what the corrections changed. A model copying the reports
could reword them, so this hook keeps them and adds them to the checker's request itself, as
review_relay.py does for documents.

Claude Code runs it on PreToolUse for the Agent tool, on PostToolUse for the Agent tool, a
subagent's SubagentHandback tool and the question tool (AskUserQuestion), on SubagentStop and on
UserPromptSubmit. It acts only in a session where the build skill was started (recorded by
build_session.py), and keeps:

- the report of the agent that runs Claude Code's `/code-review`: an agent whose request's first
  line is `Document: <plan>` and whose second line starts `Run /code-review`;
- the report of the agent that runs `/security-review`: the same, with a second line that starts
  `Run /security-review`;
- the report of the `build-reviewer` agent, whose request's first line is `Document: <plan>`.

In a Claude project thread an agent's report is the one it handed back, not the tool's text,
which there only says where the report went. Each is kept with the commit checked out when it ran,
in the repository holding the plan its `Document:` line names, found as every hook finds one
(docs/adrs/0046, repository.py), so it works when the repositories sit one level below the session
folder, as in a Claude project thread. A report of a later commit, or of a plan in another
repository, starts a new set, so the checker only ever gets reports of one commit.

Before the `build-correction-checker` starts, it appends the three reports, the reviewed commit,
the lines the build changed from where the branch left the default branch up to the commit being
checked, file by file (docs/adrs/0061), and the rubric to read, between fixed `=== ... ===` lines,
and approves the start. A check after the first, once the person has answered the open findings
(docs/adrs/0060), also gets the commit the last check ran at, that check's report and the person's answers since
then,
so it judges only what changed. It refuses the start, with a reason Claude sees, when the request
has no `Document:` line, when any of the three reports of the reviewed commit is missing, when no
git repository holds the plan, when nothing has been committed since the reviews, or, after a
check, when nothing has been committed since that check.

After a check, it saves the person's answers in the build's record, read as review_relay.py reads
them for documents: on UserPromptSubmit, a message answering a question that ended "... ignore or
defer?", or a tap on a decision card offering the four choices; on PostToolUse for the question
tool, its answers to questions offering them. Once the checker has run, its report is kept beside the three reviews, with the
plan they were of, and `kept_reports` hands all four to hand_over.py for the build's report file
(docs/adrs/0034). A review agent may run in the background, which Claude Code
can choose even when the skill asks for the foreground: its PostToolUse event then only says it
was launched, with its id, so the hook keeps the report from the event with that id that says
the agent finished: in auto mode its SubagentHandback call's PostToolUse, whose report is final,
and otherwise SubagentStop (see subagent_report.py). It holds a report that arrives first until the launch is seen. Records live in
builds/<session>.json in the plugin's folder (plugin_folder.py: `agentic/` in the session's scratchpad), and are deleted once hand_over.py has copied their
reports into the build's report file, or once unchanged for 30 days (see saved_records.py), not
when the session ends, since a resumed session carries on. Anything else,
and any input it cannot read, is left alone.
"""

import argparse
import contextlib
import json
import os
import re
import subprocess
import sys

try:
    import fcntl
except ImportError:  # Windows: run without the lock rather than fail every agent start.
    fcntl = None

import build_session
import repository
import review_relay
import saved_records
import subagent_report
import plugin_folder

ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RUBRIC = os.path.join(ROOT, "skills", "build", "references", "rubric.md")
CHECKER = "build-correction-checker"
# The agent types a review runs as. Both skill reviews run in an agent, never through the Skill
# tool: depending on the Claude Code version, /code-review run by the Skill tool either forks or
# runs inside the session and reports through a tool of its own, so its findings may never reach
# a hook (issue #79). An agent's report reaches it either way.
STOPPING = {"build-reviewer": ("plan",), "general-purpose": ("code", "security"), CHECKER: ("check",)}
PARTS = (("code", "CODE REVIEW REPORT"), ("security", "SECURITY REVIEW REPORT"),
         ("plan", "BUILD REVIEW REPORT"))


def repository_of(prompt, cwd):
    """The repository holding the plan the request's `Document:` line names (docs/adrs/0046)."""
    named, _ = first_lines(prompt)
    return repository.repository_of(named, base=cwd) if named else None


def head(folder):
    if not folder:
        return None
    try:
        result = subprocess.run(["git", "-C", folder, "rev-parse", "HEAD"], capture_output=True, text=True)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def record_path(session, data=None):
    data = data if data is not None else plugin_folder.current()
    if not data:
        return None
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session)
    return os.path.join(data, "builds", safe + ".json")


@contextlib.contextmanager
def locked(session):
    """Hold the session's lock: the three reviews start and finish side by side.

    Untested, since only a race could show it and no test relies on timing (AGENTS.md rule 5)."""
    path = record_path(session)
    if not path or not fcntl:
        yield
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".lock", "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def load(session, data=None):
    try:
        with open(record_path(session, data), encoding="utf-8") as f:
            record = json.load(f)
    except (OSError, TypeError, ValueError):
        return None
    return record if isinstance(record, dict) and isinstance(record.get("reports"), dict) else None


def save(session, record):
    path = record_path(session)
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f)
    saved_records.prune(os.path.dirname(path))


def for_commit(session, commit, folder, plan):
    record = load(session)
    if not record or record.get("commit") != commit or record.get("repository", folder) != folder:
        record = {"commit": commit, "repository": folder, "reports": {}, "started": {}}
    record.setdefault("started", {})
    record["plan"] = plan
    return record


def kept_reports(data, session, plan, cwd=None):
    """The reports kept for the session's build of `plan`, {part: text} with parts `code`,
    `security`, `plan` and `check`, for hand_over.py's report file; None when no record is kept or
    it is of another plan."""
    record = load(session, data)
    if not record or not plan or record.get("plan") != repository.full_path(plan, base=cwd):
        return None
    return {part: text for part, text in record["reports"].items() if isinstance(text, str)}


def clear(data, session):
    """Forget the session's build record once hand_over.py has copied its reports, so a later
    build in the same session never shows them as its own."""
    path = record_path(session, data)
    try:
        if path:
            os.remove(path)
    except OSError:
        pass


def first_lines(prompt):
    lines = prompt.strip().splitlines() if isinstance(prompt, str) else []
    named = lines[0][len("Document:"):].strip() if lines and lines[0].startswith("Document:") else None
    return named, (lines[1].strip() if len(lines) > 1 else "")


def part_of(tool_input):
    agent = str(tool_input.get("subagent_type") or "general-purpose").split(":")[-1]
    named, second = first_lines(tool_input.get("prompt"))
    if not named:
        return None
    if agent == "build-reviewer":
        return "plan"
    if agent == "general-purpose" and second.startswith("Run /security-review"):
        return "security"
    if agent == "general-purpose" and second.startswith("Run /code-review"):
        return "code"
    return None


def text_of(response):
    """The agent's report; one handed back in a Claude project thread, as review_relay.py."""
    if isinstance(response, dict):
        if "handback" in response or "handbackReport" in response:
            report = response.get("handbackReport")
            text = report.get("text") if isinstance(report, dict) else None
            return text if isinstance(text, str) else ""
        if isinstance(response.get("result"), str):
            return response["result"]
        blocks = response.get("content") or []
        return "".join(b.get("text") or "" for b in blocks if isinstance(b, dict))
    return response if isinstance(response, str) else ""


def refuse(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def start_checker(session, tool_input, cwd, call="check"):
    prompt = tool_input.get("prompt") or ""
    named, _ = first_lines(prompt)
    if not named:
        return refuse("Start the build correction checker with `Document: <plan path>` as the "
                      "first line of its request, the same line the build reviewer was given.")
    record = load(session)
    missing = [title.lower().replace(" report", "") for part, title in PARTS
               if not record or part not in record["reports"]]
    if missing:
        return refuse(f"No {' or '.join(missing)} report of the reviewed commit is on record in this "
                      "session, so the corrections cannot be checked. Do not review again: stop "
                      "and show the person the reports you have and this reason.")
    # A record saved before the repository was kept beside the commit names none: the checker's
    # own `Document:` line names the same plan.
    folder = record.get("repository") or repository_of(prompt, cwd)
    current = head(folder)
    if record["commit"] is None or current is None:
        return refuse(f"There is no git repository holding {named}, so the commit the reviews saw "
                      "could not be recorded and the corrections cannot be checked. Do not review "
                      "again: stop and show the person this reason.")
    if current == record["commit"]:
        return refuse("Nothing has been committed since the reviews. Commit the corrections "
                      "first, then start the build correction checker.")
    last = record.get("last_checked") if record.get("checked") else None
    if last and current == last:
        return refuse("Nothing has been committed since the last check, so there is nothing new "
                      "to check. Make the fixes the person chose and commit them first, or go on "
                      "to the next question.")
    answers = review_relay.answers_of(record) if last else []
    try:
        with locked(session):
            fresh = load(session) or record
            runs(fresh, "started")[call] = "check"
            fresh["checking"] = current
            save(session, fresh)
    except OSError:  # the checker still gets the reports; only its own report goes unkept
        pass
    build_session.answers_go_to(session, "build")
    blocks = [f"=== {title} ===\n{record['reports'][part]}\n=== END {title} ==="
              for part, title in PARTS]
    extra = (f"\n\n=== REVIEWED COMMIT ===\nReviewed commit: {record['commit']}\n"
             "=== END REVIEWED COMMIT ===\n\n" + "\n\n".join(blocks))
    if last:
        extra += (f"\n\n=== LAST CHECKED COMMIT ===\nLast checked commit: {last}\n"
                  "=== END LAST CHECKED COMMIT ===")
        extra += f"\n\n=== LAST CHECK REPORT ===\n{record['reports'].get('check', '(none)')}\n=== END LAST CHECK REPORT ==="
    if answers:
        extra += ("\n\n=== ANSWERS ===\n" + "\n".join(f"Question: {a['question']}\nAnswer: {a['answer']}\n"
                                                    for a in answers) + "=== END ANSWERS ===")
    try:
        changed = changed_lines(folder, current)
    except Exception:  # a diff this cannot read must not leave the checker without its reports
        changed = ["Not known: the build's changes could not be read."]
    extra += ("\n\n=== CHANGED LINES ===\n" + "".join(f"{line}\n" for line in changed) +
              "=== END CHANGED LINES ===\n")
    extra += f"\n=== FILES TO READ ===\nRubric: {RUBRIC}\n=== END FILES TO READ ===\n"
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow",
                                   "updatedInput": dict(tool_input, prompt=prompt + extra)}}


HUNK = re.compile(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@")


def git_out(folder, *args):
    try:
        result = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True)
    except OSError:
        return None
    return result.stdout if result.returncode == 0 else None


def changed_lines(folder, commit):
    """The lines the build changed up to `commit`, one line per file, such as
    `src/parser.ts: 3-4, 11` or `src/lookup.ts: all (new file)`, from the branch's merge base with
    the default branch (docs/adrs/0061). A deleted file, or one whose changes only remove lines,
    is left out."""
    default = (git_out(folder, "symbolic-ref", "-q", "refs/remotes/origin/HEAD") or "").strip()
    base = (git_out(folder, "merge-base", default, commit) or "").strip() if default else ""
    if not base:
        return ["Not known: git does not name the default branch (origin/HEAD)."]
    diff = git_out(folder, "-c", "core.quotePath=false", "diff", "-U0", "--no-color", "--no-ext-diff",
                   "--no-renames", "--src-prefix=a/", "--dst-prefix=b/", base, commit) or ""
    files, name, new, header = {}, None, False, False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            name, new, header = None, False, True
        elif header and line.startswith("--- "):
            new = line == "--- /dev/null"
        elif header and line.startswith("+++ "):
            path = line[len("+++ "):].rstrip("\t")  # git ends a name holding a space with a tab
            if path.startswith('"') and path.endswith('"'):
                # With core.quotePath off, git quotes only a name holding a quote, a backslash or a
                # control character.
                path = re.sub(r'\\(.)', r"\1", path[1:-1])
            name = None if path == "/dev/null" else path[len("b/"):]
            if name is not None:
                files.setdefault(name, "all (new file)" if new else [])
        elif line.startswith("@@"):
            header = False
            hunk = HUNK.match(line)
            if hunk and name is not None and not new:
                start, count = int(hunk.group(1)), int(hunk.group(2) or 1)
                if count:
                    files[name].append(str(start) if count == 1 else f"{start}-{start + count - 1}")
    return [f"{name}: {spans if isinstance(spans, str) else ', '.join(spans)}"
            for name, spans in sorted(files.items()) if spans]


def keep_answers(session, answers):
    """Add the person's answers, after a correction check, for the next check (docs/adrs/0060)."""
    if not answers or not record_path(session):
        return None
    with locked(session):
        record = load(session)
        if record and record.get("checked") and build_session.answers_to(session) == "build":
            record["answers"] = review_relay.answers_of(record) + answers
            save(session, record)
    return None


def runs(record, key):
    """The record's background runs: `launched` maps an agent's id to its call, and `stopped`
    holds the report of an agent that finished before its launch was seen."""
    if not isinstance(record.get(key), dict):
        record[key] = {}
    return record[key]


def keep(record, call, part, report):
    if record["started"].get(call) == part and report.strip():
        record["reports"][part] = report
        if part == "check":
            # Only a check that reported counts as done: the next judges what follows its commit,
            # with the answers given after it (docs/adrs/0060).
            record["checked"] = True
            if record.get("checking"):
                record["last_checked"] = record.pop("checking")
            record["answers"] = []


def agent_stopped(session, event):
    """A background review agent finished, by handing its report back or by stopping: keep its
    report, or hold it until its launch is seen while a review of its kind has no report yet. The
    launch's note is kept, so if the agent stops again, as when another hook kept it going, its
    last report is the one kept. A hand-back ends the agent's run, so once its report is in, a later
    stop, whose last message is then at most a line written beside the hand-back, is left alone."""
    agent_id = event.get("agent_id")
    parts = STOPPING.get(str(event.get("agent_type") or "").split(":")[-1])
    if (not isinstance(agent_id, str) or not agent_id or not parts
            or not build_session.building(session) or not record_path(session)):
        return None
    handed = subagent_report.handed_back_report(event) is not None
    with locked(session):
        record = load(session)
        if not record or not isinstance(record.get("started"), dict):
            return None
        launched, stopped = runs(record, "launched"), runs(record, "stopped")
        final = runs(record, "handed_back")
        if final.get(agent_id) and not handed:
            return None
        call = launched.get(agent_id)
        if isinstance(call, str):
            keep(record, call, record["started"].get(call), subagent_report.report(event))
        elif any(p in record["started"].values() and p not in record["reports"] for p in parts):
            # More room than review_relay.py holds: /code-review starts a dozen agents of its own,
            # all general-purpose, whose stops must not push out a review's held report.
            subagent_report.hold(stopped, agent_id, subagent_report.report(event), limit=50)
        else:
            return None
        if handed:
            final[agent_id] = True
        # Marks matter only while the agent's launch or held report is on record.
        for old in [k for k in final if k not in launched and k not in stopped]:
            del final[old]
        save(session, record)
    return None


def returned(record, call, part, response):
    """Keep the report an agent's tool result carries, or note its background launch."""
    agent_id = subagent_report.launched_id(response)
    if agent_id is None:
        report = text_of(response)
        runs(record, "stopped").pop(str(subagent_report.agent_id(response)), None)
    else:
        launched, stopped = runs(record, "launched"), runs(record, "stopped")
        report = stopped.pop(agent_id, None)
        launched[agent_id] = call  # so a later report of the agent is kept too
        if not isinstance(report, str):
            report = ""
    keep(record, call, part, report)


def handle(event):
    session = str(event.get("session_id") or "unknown")
    when = event.get("hook_event_name")
    if subagent_report.finished(event):
        return agent_stopped(session, event)
    if when == "UserPromptSubmit" and build_session.building(session):
        return keep_answers(session, review_relay.message_answer(event))
    if when == "PostToolUse" and event.get("tool_name") == "AskUserQuestion" and build_session.building(session):
        return keep_answers(session, review_relay.tool_answers(event))
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    tool = event.get("tool_name")
    checker = str(tool_input.get("subagent_type") or "").split(":")[-1] == CHECKER
    if tool in ("Agent", "Task") and checker:
        if when == "PreToolUse":
            return start_checker(session, tool_input, event.get("cwd"), str(event.get("tool_use_id") or "check"))
        if when == "PostToolUse":
            # Each check is of the commit it started at; the next checks only what follows it.
            # The record stays, with the check's report, for the hand-over's report file.
            with locked(session):
                record = load(session)
                if record:
                    returned(record, str(event.get("tool_use_id") or "check"), "check",
                             event.get("tool_response"))
                    save(session, record)
        return None
    if not build_session.building(session) or not record_path(session):
        return None
    if tool not in ("Agent", "Task"):
        return None
    part = part_of(tool_input)
    if not part:
        return None
    call = str(event.get("tool_use_id") or part)
    with locked(session):
        if when == "PreToolUse":
            folder = repository_of(tool_input.get("prompt"), event.get("cwd"))
            commit = head(folder)
            kept = load(session)
            if commit is None and kept and kept.get("commit"):
                # A review whose plan no repository holds must not wipe the others' reports.
                folder, commit = kept.get("repository", folder), kept["commit"]
            named, _ = first_lines(tool_input.get("prompt"))
            record = for_commit(session, commit, folder, repository.full_path(named, base=event.get("cwd")))
            record["started"][call] = part
            save(session, record)
        elif when == "PostToolUse":
            record = load(session)
            if not record or not isinstance(record.get("started"), dict):
                return None
            returned(record, call, part, event.get("tool_response"))
            save(session, record)
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1] + "\nReads one hook event as JSON from stdin. Prints a "
               "PreToolUse decision as JSON, or nothing. Always exits 0.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args(argv)
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    plugin_folder.use_event(event)
    try:
        out = handle(event) if isinstance(event, dict) else None
    except Exception:  # never block a step over a fault in this hook
        out = None
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
