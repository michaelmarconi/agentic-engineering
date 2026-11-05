#!/usr/bin/env python3
"""Read a subagent's report from Claude Code's SubagentStop hook input.

Claude Code can run a review agent in the background even when the request asks for the
foreground. Its Agent tool then returns at once with a launch notice, so the report never reaches
the tool's PostToolUse event. It reaches the SubagentStop event instead, which fires when the
agent finishes. The review relay and the build relay read it from there with `report`.

The report is the agent's last message, `last_assistant_message`. In a Claude project thread an
agent hands its report back by calling its SubagentHandback tool, so the report is that call's
`message`, read from the agent's transcript (`agent_transcript_path`, one JSON entry per line).
A hand-back wins over the last message, which may be only a line written before it. A transcript
that is missing or can't be read gives no hand-back.

Both relays also need `launched_id`, which tells a launch notice from a finished run, and `hold`,
which keeps the report of an agent that finished before its launch was seen. SubagentStop fires
for foreground runs too, whose launch is never seen, so only the last few held reports are kept.

This module has no command; the hooks import it.
"""

import json

HANDBACK = "SubagentHandback"
HELD = 5  # reports held for launches not yet seen


def handed_back(path):
    """The `message` of the last SubagentHandback call in the transcript at `path`, or None."""
    if not isinstance(path, str) or not path:
        return None
    found = None
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                message = entry.get("message") if isinstance(entry, dict) else None
                blocks = message.get("content") if isinstance(message, dict) else None
                for block in blocks if isinstance(blocks, list) else []:
                    if (isinstance(block, dict) and block.get("type") == "tool_use"
                            and block.get("name") == HANDBACK and isinstance(block.get("input"), dict)
                            and isinstance(block["input"].get("message"), str)):
                        found = block["input"]["message"]
    except (OSError, ValueError):
        return None
    return found


def report(event):
    """The finished agent's report, or "" when it left none."""
    text = handed_back(event.get("agent_transcript_path"))
    if text and text.strip():
        return text
    last = event.get("last_assistant_message")
    return last if isinstance(last, str) else ""


def launched_id(response):
    """The agent's id when the Agent tool only launched it in the background, else None."""
    if isinstance(response, dict) and response.get("status") == "async_launched":
        return agent_id(response)
    return None


def agent_id(response):
    """The agent's id in an Agent tool result, or None."""
    value = response.get("agentId") if isinstance(response, dict) else None
    return value if isinstance(value, str) and value else None


def hold(held, key, value):
    """Hold `value` under `key` in the dict `held`, keeping only the newest HELD entries."""
    held.pop(key, None)
    held[key] = value
    for old in list(held)[:-HELD]:
        del held[old]
