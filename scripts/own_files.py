#!/usr/bin/env python3
"""Let the plugin's skills and agents read the plugin's own files without asking the person.

A skill reads its rubric and template, and a reviewer reads the rubric, from the plugin's
folder. That folder sits outside the person's project, so Claude Code asks permission for every
read there, and when the person can't be asked, as in a session run without them, the read is
refused and the skill works without its rubric.

/audit's agents read a diff file the audit script writes outside the project, in a temporary
folder; a routine runs with nobody to answer a prompt, so those reads must be approved too.

Claude Code runs this hook on PreToolUse for Read, Glob and Grep. It reads the hook's JSON from
stdin. When the file or folder the tool would read resolves, links followed, to a place inside
$CLAUDE_PLUGIN_ROOT, or inside sdlc-audits-<user id> in the system's temporary folder when that is a folder only this user owns and can open, it approves
the call. Anything else, including a search with no path, is left to the person's own permission
rules, so the hook never widens access beyond the plugin's own folders.
"""

import argparse
import json
import os
import stat
import sys
import tempfile

TOOLS = {"Read": "file_path", "Glob": "path", "Grep": "path"}


def inside(path, root):
    """Whether `path` resolves to `root` or a place under it."""
    path, root = os.path.realpath(path), os.path.realpath(root)
    return os.path.commonpath([path, root]) == root


def private_folder(folder):
    """Whether `folder` is a real folder, not a link, that only this user owns and can open.

    Anyone can make a folder in the temporary folder, so one made by another user, or a link to
    somewhere else, would let them choose what this hook approves.
    """
    try:
        info = os.lstat(folder)
    except OSError:
        return False
    return stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and not info.st_mode & 0o077


def allowed_roots():
    """The folders whose files the plugin's skills and agents may read without asking."""
    roots = [os.environ.get("CLAUDE_PLUGIN_ROOT", "")]
    # The audit script's fallback, as skills/audit/scripts/audit.py names it. os.getuid is missing
    # on Windows, where there is no fallback.
    if hasattr(os, "getuid"):
        fallback = os.path.join(tempfile.gettempdir(), f"sdlc-audits-{os.getuid()}")
        if private_folder(fallback):
            roots.append(fallback)
    return [root for root in roots if root]


def handle(event):
    """The hook's output for one event, or None to leave the call alone."""
    field = TOOLS.get(event.get("tool_name"))
    path = (event.get("tool_input") or {}).get(field) if field else None
    if not isinstance(path, str) or not os.path.isabs(path):
        return None
    if not any(inside(path, root) for root in allowed_roots()):
        return None
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "Reads the sdlc plugin's own files, or an audit's diff file.",
    }}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Reads one Claude Code PreToolUse event as JSON from stdin. Prints a decision that "
               "approves the call when it reads inside $CLAUDE_PLUGIN_ROOT or an audit's diff folder, "
               "and nothing otherwise. "
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
