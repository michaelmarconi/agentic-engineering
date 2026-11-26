#!/usr/bin/env python3
"""Prompt the agent to update its progress list after each helper agent (docs/adrs/0063).

Claude Code runs this as a PostToolUse hook on the `Agent` and `Task` tools, which start a helper
agent, and on `SubagentHandback`, through which a Claude project thread hands back a helper
agent's report. Most long steps of a skill run are a helper agent's run, such as a review or one
audit, so this is the moment the lifecycle page's "Showing progress" section asks for an update
(docs/adrs/0062). The note works whether the agent ran in the foreground, where its report is
already in, or in the background, where it comes later. Like card_nudge.py, its wording applies
only where a list is shown, so a skill that shows none ignores it. Every other tool passes.
"""

import argparse
import json
import sys

TOOLS = ("Agent", "Task", "SubagentHandback")
NOTE = ("If you are showing progress, then once this helper agent's report is in, update your "
        "progress list: mark the step it ran as done, with a one-line summary of what it found.")


def handle(event):
    """The hook's output for one PostToolUse event, or None when the tool started no helper agent."""
    if event.get("hook_event_name", "PostToolUse") != "PostToolUse" or event.get("tool_name") not in TOOLS:
        return None
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": NOTE}}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Reads one Claude Code PostToolUse event as JSON from stdin. Prints the note to "
               "update the progress list, as JSON, after a helper agent's tool, and nothing "
               "otherwise. Always exits 0.")
    parser.parse_args(argv)
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    out = handle(event) if isinstance(event, dict) else None
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
