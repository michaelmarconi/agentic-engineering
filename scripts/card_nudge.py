#!/usr/bin/env python3
"""Have a question the agent asked in words also posted on a decision card, as issue #146 asks.

Claude Code runs this as a PostToolUse hook on any MCP tool named `mcp__<server>__post_message`,
the tool a Claude project thread gives the agent for replying to the person. Where there is no
question tool, a skill asks each question in words ending with the line the answer hook looks for,
"Accept, give your own answer, ignore or defer?" (the lifecycle page's "Ending with your answers").
When the posted message's `text` ends with that line, this hook tells the agent, at that moment,
to post the same question on a decision card whose options are named exactly "Accept", "Ignore"
and "Defer", the proposal recommended. Exact names let the answer hook save a tap as the answer.
It keys on the line, not on a skill, so every skill that ends a question with it is covered and no
other is touched. The CLI and the desktop app have no such tool, so there the hook never runs.
Every other tool call and message passes.
"""

import argparse
import json
import re
import sys

LINE = "Accept, give your own answer, ignore or defer?"
TOOL = re.compile(r"^mcp__.+__post_message$")
NUDGE = (
    "You just asked the person a question in words, ending \"" + LINE + "\". Now post the same "
    "question on a decision card, unless you already have this turn: options named exactly "
    "\"Accept\", \"Ignore\" and \"Defer\", with any detail in each option's description rather "
    "than its name, and \"Accept\" (your proposal) recommended. Then end your turn and wait for "
    "the answer.")


def handle(event):
    """The hook's output for one PostToolUse event, or None when the call needs no card."""
    if not TOOL.match(str(event.get("tool_name", ""))):
        return None
    tool_input = event.get("tool_input")
    text = tool_input.get("text") if isinstance(tool_input, dict) else None
    if not isinstance(text, str) or not text.rstrip().endswith(LINE):
        return None
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": NUDGE}}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Reads one Claude Code PostToolUse event as JSON from stdin. Prints the instruction "
               "to post a decision card, as JSON, when a posted message ends with the asking "
               "line, and nothing otherwise. Always exits 0.")
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
