#!/usr/bin/env python3
"""Let /build start only in answer to the first message the person sends in a session.

Claude Code runs this on four hook events:

- SessionStart: a session that starts new, or after /clear (which gives it a new session id),
  is recorded as fresh, with no messages yet. One that is resumed is recorded as not fresh,
  since its earlier conversation is back in context. Compaction keeps what was recorded.
- UserPromptSubmit: each message from the person is counted. In a Claude project thread,
  messages arrive wrapped in a `<wake>` envelope; only one that holds a message `from="human"`
  counts, so the note that opens a thread and events such as a pull request closing do not.
  A typed `/build` or `/sdlc:build` is blocked unless it is the first message counted.
- PreToolUse on Skill: starting `build` or `sdlc:build` is refused unless the session is fresh
  and exactly one message has been counted, which covers asking in plain words.
- SessionEnd: the session's record is deleted.

Records live in $CLAUDE_PLUGIN_DATA/sessions/<session id>.json. Without $CLAUDE_PLUGIN_DATA, or
when the input cannot be read, nothing is recorded and /build is refused, since freshness
cannot be shown; nothing else is ever blocked.
"""

import argparse
import json
import os
import re
import sys

BUILD_SKILLS = ("build", "sdlc:build")
TYPED_BUILD = re.compile(r"^\s*/(?:sdlc:)?build(?:\s|$)")
REASON = (
    "/build starts only in answer to the first message in a new session, or the first after "
    "/clear, so the build begins with a clean context and the written plan. Start a new session "
    "(in a Claude project, a new thread) and ask for the build as your first message."
)


def folder():
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    return os.path.join(data, "sessions") if data else None


def record_path(session):
    where = folder()
    if not where or not session:
        return None
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", str(session))
    return os.path.join(where, safe + ".json")


def load(session):
    path = record_path(session)
    if not path:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save(session, record):
    path = record_path(session)
    if not path:
        return
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f)
    except OSError:
        pass


def from_person(prompt):
    """True if the prompt is a message the person sent, not a thread's opening note or an event."""
    text = prompt.lstrip()
    if not text.startswith("<wake"):
        return True
    return bool(re.search(r'<message\b[^>]*\bfrom="human"', text))


def fresh(record):
    return bool(record) and record.get("fresh") is True and record.get("messages") == 1


def on_start(event):
    session = event.get("session_id")
    source = event.get("source")
    if source in ("startup", "clear"):
        save(session, {"fresh": True, "messages": 0})
    elif source == "compact" and load(session):
        return None
    else:
        save(session, {"fresh": False, "messages": 0})
    return None


def on_prompt(event):
    session = event.get("session_id")
    prompt = str(event.get("prompt") or "")
    record = load(session) or {"fresh": False, "messages": 0}
    if from_person(prompt):
        record["messages"] = record.get("messages", 0) + 1
        save(session, record)
    if TYPED_BUILD.match(prompt) and not fresh(record):
        return {"decision": "block", "reason": REASON}
    return None


def on_skill(event):
    tool_input = event.get("tool_input") or {}
    if not isinstance(tool_input, dict) or tool_input.get("skill") not in BUILD_SKILLS:
        return None
    if fresh(load(event.get("session_id"))):
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": REASON}}


def on_end(event):
    path = record_path(event.get("session_id"))
    if path:
        try:
            os.remove(path)
        except OSError:
            pass
    return None


HANDLERS = {"SessionStart": on_start, "UserPromptSubmit": on_prompt, "PreToolUse": on_skill,
            "SessionEnd": on_end}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1] + "\nReads one hook event as JSON from stdin. "
               "Prints a hook decision as JSON, or nothing. Always exits 0.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args(argv)
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(event, dict):
        return 0
    handler = HANDLERS.get(event.get("hook_event_name"))
    result = handler(event) if handler else None
    if result:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
