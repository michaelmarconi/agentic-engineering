#!/usr/bin/env python3
"""Keep the reports of /verify's agents, so `verify.py report` can put them in the run's report
file word for word (ADR 0034), and the commit the run checks.

Claude Code runs it on PostToolUse for the Agent tool and a subagent's SubagentHandback tool, and
on SubagentStop. It keeps the report of each `verifier` and `verify-checker` agent, keyed by the
agent's type and the spec on its request's `Document:` line. An agent run again for the same spec
replaces its earlier report. It is kept the way audit_relay.py keeps an audit's agents, and with
that script's code: in a Claude project thread the report is the one the agent handed back, and an
agent that runs in the background is kept from the event that says it finished, joined to its
launch by its id.

Records live in $CLAUDE_PLUGIN_DATA/verifies/<session>.json and are deleted once unchanged for 30
days (see saved_records.py), or when `verify.py start` or `verify.py report` clears them. `verify.py
start` also keeps the commit it found there. Without $CLAUDE_PLUGIN_DATA nothing is kept. It
changes no request, refuses nothing and prints nothing.
"""

import argparse
import json
import os
import re
import sys

import subagent_report
from audit_relay import keep, load, locked, save
from build_relay import text_of

AGENTS = ("verifier", "verify-checker")
HELD = 20  # a run starts one verifier and one checker per spec


def record_path(data, session):
    if not data:
        return None
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", str(session))
    return os.path.join(data, "verifies", safe + ".json")


def reports(data, session):
    """The session's kept reports, in the order they were first kept: [{agent, document, kind, text}]."""
    path = record_path(data, session)
    return list(load(path)["reports"].values()) if path else []


def clear(data, session):
    path = record_path(data, session)
    if path and os.path.exists(path):
        os.remove(path)


def set_commit(data, session, commit):
    """Keep the commit a run checks, beside its agents' reports."""
    path = record_path(data, session)
    if not path:
        return
    with locked(path):
        record = load(path)
        record["commit"] = commit
        save(path, record)


def commit(data, session):
    """The commit `set_commit` kept, or None."""
    path = record_path(data, session)
    value = load(path).get("commit") if path else None
    return value if isinstance(value, str) and value else None


def agent_type(value):
    name = str(value or "").split(":")[-1]
    return name if name in AGENTS else None


def identity(tool_input):
    """{agent, document, kind} for a verify agent's request, or None for any other agent."""
    agent = agent_type(tool_input.get("subagent_type"))
    if not agent:
        return None
    prompt = tool_input.get("prompt") if isinstance(tool_input.get("prompt"), str) else ""
    first = prompt.strip().splitlines()[0] if prompt.strip() else ""
    document = first[len("Document:"):].strip() if first.startswith("Document:") else ""
    return {"agent": agent, "document": document, "kind": ""}


def finished(record, event):
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
        subagent_report.hold(record["stopped"], agent_id, text, limit=HELD)
    if handed:
        record["final"][agent_id] = True
    return True


def returned(record, tool_input, response):
    who = identity(tool_input)
    if not who:
        return False
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
    path = record_path(os.environ.get("CLAUDE_PLUGIN_DATA"), event.get("session_id") or "unknown")
    if not path:
        return
    if subagent_report.finished(event):
        if not agent_type(event.get("agent_type")):
            return
        with locked(path):
            record = load(path)
            if finished(record, event):
                save(path, record)
        return
    tool_input = event.get("tool_input")
    if (event.get("hook_event_name") != "PostToolUse" or event.get("tool_name") not in ("Agent", "Task")
            or not isinstance(tool_input, dict) or not identity(tool_input)):
        return
    with locked(path):
        record = load(path)
        if returned(record, tool_input, event.get("tool_response")):
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
    try:
        if isinstance(event, dict):
            handle(event)
    except Exception:  # never block a step over a fault in this hook
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
