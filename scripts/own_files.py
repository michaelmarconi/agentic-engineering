#!/usr/bin/env python3
"""Let the plugin's skills and agents read the plugin's own files without asking the person.

A skill reads its rubric and template, and a reviewer reads the rubric, from the plugin's
folder. That folder sits outside the person's project, so Claude Code asks permission for every
read there, and when the person can't be asked, as in a session run without them, the read is
refused and the skill works without its rubric.

Claude Code runs this hook on PreToolUse for Read, Glob and Grep. It reads the hook's JSON from
stdin. When the file or folder the tool would read resolves, links followed, to a place inside
$CLAUDE_PLUGIN_ROOT, it approves the call. Anything else, including a search with no path, is
left to the person's own permission rules, so the hook never widens access beyond the plugin.
"""

import argparse
import json
import os
import sys

TOOLS = {"Read": "file_path", "Glob": "path", "Grep": "path"}


def inside(path, root):
    """Whether `path` resolves to `root` or a place under it."""
    path, root = os.path.realpath(path), os.path.realpath(root)
    return os.path.commonpath([path, root]) == root


def handle(event):
    """The hook's output for one event, or None to leave the call alone."""
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    field = TOOLS.get(event.get("tool_name"))
    path = (event.get("tool_input") or {}).get(field) if field else None
    if not root or not isinstance(path, str) or not os.path.isabs(path) or not inside(path, root):
        return None
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "Reads the sdlc plugin's own files.",
    }}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Reads one Claude Code PreToolUse event as JSON from stdin. Prints a decision that "
               "approves the call when it reads inside $CLAUDE_PLUGIN_ROOT, and nothing otherwise. "
               "Always exits 0.")
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
