#!/usr/bin/env python3
"""Tell Claude how much conversation a session has gained when a build starts (docs/adrs/0037).

Claude Code runs this on two hook events:

- PreToolUse on Skill: when Claude starts `build` or `agentic:build`.
- UserPromptSubmit: when the person types `/build` or `/agentic:build`.

Each time, it measures how much conversation the session has gained since Claude's first reply,
and gives Claude that figure, the limit of 20,000 tokens and whether the session is over it, as
added context. The build skill asks the person whether to build here anyway when it is over. The
hook never refuses a build: a long session is only a reason to ask.

The measure comes from the session's record, the file Claude Code names in `transcript_path`.
Each reply from Claude in it carries the context it used: input_tokens, cache_read_input_tokens
and cache_creation_input_tokens added up. Lines from sub-agents (`isSidechain`) are skipped. The
growth is the latest reply's figure minus the first's, counting from the first reply after the
last compaction, if any, so conversation added since then is not hidden. With no reply yet, or no record written yet, it
is 0; a record that cannot be read is reported as not measured. On PreToolUse, Claude Code has not yet written the reply holding the Skill call, so
the figure may be one reply behind.

Every start of the build skill is recorded, so the branch guard knows a build may be running; that
includes one the person then chooses not to run here, which only keeps the guard on in that session. The record is
kept when the session ends or is resumed, since a resumed session carries on, and is deleted once
unchanged for 30 days (see saved_records.py). Records live in
$CLAUDE_PLUGIN_DATA/sessions/<session id>.json; without $CLAUDE_PLUGIN_DATA nothing is recorded.
"""

import argparse
import json
import os
import re
import sys

import saved_records

BUILD_SKILLS = ("build", "agentic:build")
TYPED_BUILD = re.compile(r"^\s*/(?:agentic:)?build(?:\s|$)")
LIMIT = 20000
USAGE = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


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
        return
    saved_records.prune(os.path.dirname(path))


def building(session):
    """True if a build was started in this session, for the branch guard."""
    record = load(session)
    return isinstance(record, dict) and record.get("building") is True


def context_used(line):
    """The context one of Claude's own replies used, or None for any other line."""
    if not isinstance(line, dict) or line.get("type") != "assistant" or line.get("isSidechain"):
        return None
    message = line.get("message")
    usage = message.get("usage") if isinstance(message, dict) else None
    if not isinstance(usage, dict):
        return None
    total = sum(usage[key] for key in USAGE if isinstance(usage.get(key), int))
    return total or None


def growth(transcript):
    """Tokens of context gained since Claude's first reply, or since the last compaction; None if
    the session's record cannot be read."""
    if not transcript:
        return None
    first = latest = None
    try:
        with open(transcript, encoding="utf-8") as f:
            for text in f:
                if '"usage"' not in text and '"compact_boundary"' not in text:
                    continue  # most lines are tool output, not worth parsing
                try:
                    line = json.loads(text)
                except ValueError:
                    continue
                if isinstance(line, dict) and line.get("subtype") == "compact_boundary":
                    first = latest = None
                    continue
                used = context_used(line)
                if used is not None:
                    first = used if first is None else first
                    latest = used
    except FileNotFoundError:
        return 0  # Claude Code writes the record with its first reply, so there is none yet
    except OSError:
        return None
    return max(latest - first, 0) if first is not None else 0


def note(gained):
    if gained is None:
        return ("Build session check (agentic plugin): how much conversation this session has "
                "gained could not be measured, since its record could not be read.")
    side = "over" if gained > LIMIT else "under"
    return (f"Build session check (agentic plugin): this session has gained {gained:,} tokens of "
            f"conversation since Claude's first reply, {side} the limit of {LIMIT:,}.")


def start_build(event, hook_event):
    session = event.get("session_id")
    record = load(session)
    record = record if isinstance(record, dict) else {}
    record["building"] = True
    save(session, record)
    return {"hookSpecificOutput": {"hookEventName": hook_event,
                                   "additionalContext": note(growth(event.get("transcript_path")))}}


def on_prompt(event):
    if TYPED_BUILD.match(str(event.get("prompt") or "")):
        return start_build(event, "UserPromptSubmit")
    return None


def on_skill(event):
    tool_input = event.get("tool_input") or {}
    if isinstance(tool_input, dict) and tool_input.get("skill") in BUILD_SKILLS:
        return start_build(event, "PreToolUse")
    return None


HANDLERS = {"UserPromptSubmit": on_prompt, "PreToolUse": on_skill}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog=__doc__.split("\n\n", 1)[1] + "\nReads one hook event as JSON from stdin. "
               "Prints the added context as hook JSON, or nothing. Always exits 0.",
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
