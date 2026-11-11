#!/usr/bin/env python3
"""Read a subagent's report when it finishes: from its SubagentHandback call, or from SubagentStop.

Claude Code can run a review agent in the background even when the request asks for the
foreground. Its Agent tool then returns at once with a launch notice, so the report never reaches
the tool's PostToolUse event. The review relay and the build relay read it, with `report`, from one
of two events that fire as the agent finishes, both carrying its `agent_id` and `agent_type`:

- In auto mode, as in the Claude desktop app and Claude project threads, an agent ends by calling
  its SubagentHandback tool with its report as the call's `message`. That call's own PostToolUse
  event carries the report, and is the one to trust: `handed_back_report` reads it. A hand-back
  ends the agent's run, so it is the agent's final report.
- SubagentStop fires when any agent finishes. Its report is the agent's last message,
  `last_assistant_message`, which after a hand-back is absent or only a line written beside the
  call. So it falls back to the hand-back's `message` in the agent's transcript
  (`agent_transcript_path`, one JSON entry per line), which Claude Code may not have written yet.
  A transcript that is missing or can't be read gives no hand-back.

Both relays also need `launched_id`, which tells a launch notice from a finished run, and `hold`,
which keeps the report of an agent that finished before its launch was seen. Both events fire for
foreground runs too, whose launch is never seen, so only the last few held reports are kept.

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


def handed_back_report(event):
    """The report in the PostToolUse event of an agent's own SubagentHandback call, or None when
    the event is not one, names no agent, or the hand-back was not sent."""
    if not (isinstance(event, dict) and event.get("hook_event_name") == "PostToolUse"
            and event.get("tool_name") == HANDBACK):
        return None
    agent_id, tool_input, response = (event.get("agent_id"), event.get("tool_input"),
                                      event.get("tool_response"))
    if not isinstance(agent_id, str) or not agent_id or not isinstance(tool_input, dict):
        return None
    if isinstance(response, dict) and response.get("success") is False:
        return None
    message = tool_input.get("message")
    return message if isinstance(message, str) and message.strip() else None


def finished(event):
    """Whether the event says an agent finished: a SubagentStop, or a hand-back that was sent."""
    return (isinstance(event, dict) and event.get("hook_event_name") == "SubagentStop"
            or handed_back_report(event) is not None)


def report(event):
    """The finished agent's report, or "" when it left none."""
    message = handed_back_report(event)
    if message is not None:
        return message
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
