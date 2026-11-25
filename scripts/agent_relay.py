#!/usr/bin/env python3
"""Keep the reports of /audit's and /verify's agents, so `audit.py report` and `verify.py report`
can put them in the run's report file word for word (ADR 0034).

Claude Code runs it on PostToolUse for the Agent tool and a subagent's SubagentHandback tool, and
on SubagentStop. RUNS names each skill's agents. It keeps the report of each, keyed by the agent's
type, the document on its request's `Document:` line (none for the audit picker) and, for the
audit checker, which report it was given to check (`AUDIT REPORT` or `BRIEF REPORT`), since one
document can have both. An agent run again under the same key replaces its earlier report, and a
verifier's new report also drops the checker's report on the same spec, which was of the old one. In a
Claude project thread the report is the one the agent handed back. An agent that runs in the
background is kept from the event that says it finished, joined to its launch by its id, as
build_relay.py does (see subagent_report.py). A report that arrives before its launch is held
until the launch is seen; once an agent has handed its report back, a later stop is left alone.

Records live in audits/<session>.json or verifies/<session>.json in the plugin's folder
(plugin_folder.py: `agentic/` in the session's scratchpad), and are deleted once unchanged for 30
days (see saved_records.py), or when the skill's script clears them at `start` or `report`. With
no usable folder nothing is kept. It changes no request, refuses nothing and prints nothing.
"""

import argparse
import contextlib
import json
import os
import re
import sys

try:
    import fcntl
except ImportError:  # Windows: run without the lock rather than fail every agent start.
    fcntl = None

import saved_records
import subagent_report
import plugin_folder
from build_relay import text_of

# For each skill: its agents, the reports its checker can be given, the record folder, and how many
# early reports to hold. An audit starts one auditor and one checker per document; a verify run
# one verifier and one checker per spec.
RUNS = {
    "audit": {"agents": ("audit-picker", "auditor", "brief-checker", "audit-checker"),
              "kinds": {"audit-checker": ("AUDIT REPORT", "BRIEF REPORT")}, "folder": "audits", "held": 50},
    "verify": {"agents": ("verifier", "verify-checker"), "kinds": {}, "folder": "verifies", "held": 20},
}


def record_path(data, session, run):
    if not data:
        return None
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", str(session))
    return os.path.join(data, RUNS[run]["folder"], safe + ".json")


@contextlib.contextmanager
def locked(path):
    """Hold the record's lock: a run's agents finish side by side.

    Untested, since only a race could show it and no test relies on timing (AGENTS.md rule 5)."""
    if not fcntl:
        yield
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".lock", "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            record = json.load(f)
    except (OSError, TypeError, ValueError):
        record = None
    if not isinstance(record, dict):
        record = {}
    for key in ("reports", "launched", "stopped", "final"):
        if not isinstance(record.get(key), dict):
            record[key] = {}
    return record


def save(path, record):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f)
    saved_records.prune(os.path.dirname(path))


def reports(data, session, run):
    """The session's kept reports of one skill's agents, in the order they were first kept:
    [{agent, document, kind, requested, text}]."""
    path = record_path(data, session, run)
    return list(load(path)["reports"].values()) if path else []


def clear(data, session, run):
    path = record_path(data, session, run)
    if path and os.path.exists(path):
        os.remove(path)


def run_of(value):
    """(skill, agent) for one of RUNS' agents, such as "agentic:auditor", or (None, None)."""
    name = str(value or "").split(":")[-1]
    return next(((run, name) for run, spec in RUNS.items() if name in spec["agents"]), (None, None))


def identity(tool_input):
    """(skill, {agent, document, kind, requested}) for one of RUNS' agents' requests, or (None, None)."""
    run, agent = run_of(tool_input.get("subagent_type"))
    if not agent:
        return None, None
    prompt = tool_input.get("prompt") if isinstance(tool_input.get("prompt"), str) else ""
    first = prompt.strip().splitlines()[0] if prompt.strip() else ""
    document = first[len("Document:"):].strip() if first.startswith("Document:") else ""
    kind = next((k for k in RUNS[run]["kinds"].get(agent, ()) if f"=== {k} ===" in prompt), "")
    return run, {"agent": agent, "document": document, "kind": kind, "requested": requested(prompt)}


def requested(prompt):
    """[[number, name]] for the `<number>. <name>` lines under a request's `Requirements:` line, as
    the verify skill names the requirements a verifier is to check, so `verify.py report` can list
    them as not checked when the verifier checked nothing."""
    found, listing = [], False
    for line in prompt.splitlines():
        if line.strip() == "Requirements:":
            listing = True
            continue
        match = re.match(r"^\s*(\d+)\.\s+(\S.*?)\s*$", line) if listing else None
        if not match:
            if listing and line.strip():
                break
            continue
        found.append([int(match.group(1)), match.group(2)])
    return found


def keep(record, who, text):
    if isinstance(text, str) and text.strip():
        key = "|".join((who["agent"], who["document"], who["kind"]))
        record["reports"].pop(key, None)
        if who["agent"] == "verifier":  # a checker's report is of the verifier's report it was given
            record["reports"].pop("|".join(("verify-checker", who["document"], "")), None)
        record["reports"][key] = dict(who, text=text)


def finished(record, event, run):
    agent_id = event.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        return False
    handed = subagent_report.handed_back_report(event) is not None
    if record["final"].get(agent_id) and not handed:
        return False
    text = subagent_report.report(event)
    who = record["launched"].get(agent_id)
    if isinstance(who, dict):
        keep(record, who, text)
    else:
        subagent_report.hold(record["stopped"], agent_id, text, limit=RUNS[run]["held"])
    if handed:
        record["final"][agent_id] = True
    return True


def returned(record, who, response):
    launched = subagent_report.launched_id(response)
    if launched is None:
        record["stopped"].pop(str(subagent_report.agent_id(response)), None)
        keep(record, who, text_of(response))
    else:
        record["launched"][launched] = who
        held = record["stopped"].pop(launched, None)
        keep(record, who, held)
    return True


def handle(event):
    session = event.get("session_id") or "unknown"
    if subagent_report.finished(event):
        run, _ = run_of(event.get("agent_type"))
        path = run and record_path(plugin_folder.current(), session, run)
        if not path:
            return
        with locked(path):
            record = load(path)
            if finished(record, event, run):
                save(path, record)
        return
    tool_input = event.get("tool_input")
    if (event.get("hook_event_name") != "PostToolUse" or event.get("tool_name") not in ("Agent", "Task")
            or not isinstance(tool_input, dict)):
        return
    run, who = identity(tool_input)
    path = run and record_path(plugin_folder.current(), session, run)
    if not path:
        return
    with locked(path):
        record = load(path)
        if returned(record, who, event.get("tool_response")):
            save(path, record)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1] + "\nReads one hook event as JSON from stdin. Prints "
               "nothing. Always exits 0.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args(argv)
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    plugin_folder.use_event(event)
    try:
        if isinstance(event, dict):
            handle(event)
    except Exception:  # never block a step over a fault in this hook
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
