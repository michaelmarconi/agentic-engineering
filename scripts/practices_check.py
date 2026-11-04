#!/usr/bin/env python3
"""Keep recorded practices short and free of imports, as docs/adrs/0019 decides.

Claude Code runs this as a PreToolUse hook on Write, Edit and MultiEdit. It reads the hook's
JSON from stdin and works out what the file would hold after the edit. It checks two kinds of
file, relative to the project ($CLAUDE_PROJECT_DIR, or the current directory if unset):

- `AGENTS.md` at the project's root: its `## Practices` section, from that heading to the next
  `## ` heading, trailing blank lines left out, may be at most 50 lines.
- Each Markdown file under `docs/practices/`: at most 200 lines.

In either, a line that starts with `@` (spaces before it allowed, code blocks left out) is an
import, which makes Claude load the whole named file into every session; none may be added.

The hook refuses an edit only when it makes things worse: a file that ends over its limit and
longer than before, or that holds more imports than before. So a file already too long can still
be shortened or changed. Every other file, tool and input is left alone, and an edit whose text
cannot be found is left for the tool itself to reject.
"""

import argparse
import json
import os
import re
import sys

CORE_LIMIT = 50
TOPIC_LIMIT = 200
IMPORT = re.compile(r"^\s*@\S")
FENCE = re.compile(r"^\s*(```|~~~)")


def project():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def kind(path):
    """'core' for the root AGENTS.md, 'topic' for a Markdown file under docs/practices/, else None."""
    full = path if os.path.isabs(path) else os.path.join(project(), path)
    rel = os.path.relpath(os.path.normpath(full), project()).replace(os.sep, "/")
    if rel == "AGENTS.md":
        return "core"
    if rel.startswith("docs/practices/") and rel.endswith(".md"):
        return "topic"
    return None


def core(text):
    """The lines of the ## Practices section, from its heading to the next ## heading."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.fullmatch(r"## Practices\s*", l)), None)
    if start is None:
        return []
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    part = lines[start:end]
    while part and not part[-1].strip():
        part.pop()
    return part


def imports(lines):
    count, fenced = 0, False
    for line in lines:
        if FENCE.match(line):
            fenced = not fenced
        elif not fenced and IMPORT.match(line):
            count += 1
    return count


def after(tool, tool_input, before):
    """The file's text after the edit, or None when it can't be worked out."""
    if tool == "Write":
        content = tool_input.get("content")
        return content if isinstance(content, str) else None
    edits = [tool_input] if tool == "Edit" else tool_input.get("edits")
    if not isinstance(edits, list):
        return None
    text = before
    for edit in edits:
        old, new = (edit.get("old_string"), edit.get("new_string")) if isinstance(edit, dict) else (None, None)
        if not isinstance(old, str) or not isinstance(new, str) or old not in text:
            return None
        text = text.replace(old, new) if edit.get("replace_all") else text.replace(old, new, 1)
    return text


def refuse(reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def handle(event):
    """Return the hook's JSON output, or None to leave the edit alone."""
    if not isinstance(event, dict) or event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        return None
    tool_input = event.get("tool_input")
    path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    what = kind(path) if isinstance(path, str) and path else None
    if not what:
        return None
    full = path if os.path.isabs(path) else os.path.join(project(), path)
    try:
        with open(full, encoding="utf-8") as f:
            before = f.read()
    except (OSError, ValueError):
        before = ""
    text = after(event["tool_name"], tool_input, before)
    if text is None:
        return None
    if what == "core":
        old, new, limit = core(before), core(text), CORE_LIMIT
        place = "the ## Practices section of AGENTS.md"
        advice = ("Move detail into a topic file under docs/practices/ and leave one line in the "
                  "section saying when to read it.")
    else:
        old, new, limit = before.splitlines(), text.splitlines(), TOPIC_LIMIT
        place = path
        advice = "Keep only what an agent needs for this topic, or split it into two topics."
    if imports(new) > imports(old):
        return refuse(f"This edit adds an import (a line starting with @) to {place}. An import "
                      "loads the whole file into every session; name the file in a sentence that "
                      "says when to read it instead.")
    if len(new) > limit and len(new) > len(old):
        return refuse(f"This edit would make {place} {len(new)} lines long; the limit is {limit}. "
                      + advice)
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="Limits: the ## Practices section of AGENTS.md at most 50 lines, each file under "
               "docs/practices/ at most 200, and no @ imports in either. Reads one Claude Code "
               "PreToolUse event as JSON from stdin. Prints a refusal as JSON when an edit breaks "
               "a limit, and nothing otherwise. Always exits 0.")
    parser.parse_args(argv)
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    try:
        out = handle(event)
    except Exception:  # never block an edit over a fault in this hook
        out = None
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
