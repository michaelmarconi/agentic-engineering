#!/usr/bin/env python3
"""Refuse spec status changes the lifecycle does not allow.

Claude Code runs this as a PreToolUse hook on Write, Edit and MultiEdit. It reads the hook's
JSON from stdin and, for a *.spec.md under the project's docs/specs/ (the project being
$CLAUDE_PROJECT_DIR, or the current directory if unset), works out what the file
would contain after the edit and compares it with what is on disk now. It refuses:

- a spec that had a lifecycle status (Draft, Ready to build or Built) losing it;
- a spec that had none being given any status but Draft, so new specs start as Draft;
- setting Built: only the build step may, and it does not exist yet;
- Ready to build or Built to anything but Draft;
- Ready to build while the Open questions section is not empty or "None.";
- a change to a Ready to build or Built spec that does not return it to Draft.

A file that has no lifecycle status before or after the edit is left alone, so a project that
keeps other files under docs/specs/ is not affected. Edits made any other way, by hand or through
a shell command, are not seen.
"""

import argparse
import json
import os
import re
import sys

STATUSES = ("Draft", "Ready to build", "Built")
EMPTY_ANSWERS = {"", "none", "none."}
FOOTNOTE = re.compile(r"^\[[^\]]+\]:")


def is_spec(path):
    """True for a *.spec.md under docs/specs/ in the project ($CLAUDE_PROJECT_DIR or cwd)."""
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    relative = os.path.relpath(os.path.abspath(path), os.path.abspath(project))
    parts = os.path.normpath(relative).split(os.sep)
    return parts[:2] == ["docs", "specs"] and parts[-1].endswith(".spec.md")


def frontmatter(text):
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for end, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:end]
    return None


def status_of(text):
    for line in frontmatter(text) or []:
        if line.startswith("status:"):
            value = line[len("status:"):].split("#", 1)[0].strip()
            return value.strip("\"'")
    return None


def without_status(text):
    lines = text.lstrip("\ufeff").splitlines()
    end = len(frontmatter(text) or []) + 1
    return [line for i, line in enumerate(lines) if i > end or not line.startswith("status:")]


def has_open_questions(text):
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip().lower() == "## open questions"]
    if not starts:
        return True
    for line in lines[starts[0] + 1:]:
        if line.startswith("# ") or line.startswith("## "):
            break
        if FOOTNOTE.match(line):
            continue
        answer = line.strip().lstrip("-*").strip().strip("_*").strip().lower()
        if answer not in EMPTY_ANSWERS:
            return True
    return False


def after_edit(tool, tool_input, before):
    """Return the file's text after the edit, or None if it cannot be worked out."""
    if tool == "Write":
        return tool_input.get("content", "")
    if tool == "Edit":
        edits = [tool_input]
    elif tool == "MultiEdit":
        edits = tool_input.get("edits", [])
    else:
        return None
    text = before or ""
    for edit in edits:
        old, new = edit.get("old_string", ""), edit.get("new_string", "")
        if old == "" and text == "":
            text = new
            continue
        if not old or old not in text:
            return None
        text = text.replace(old, new) if edit.get("replace_all") else text.replace(old, new, 1)
    return text


def check(payload):
    """Return the reason to refuse the tool call, or None to allow it."""
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path", "")
    if not path or not is_spec(path):
        return None
    before = None
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                before = f.read()
        except (OSError, UnicodeDecodeError) as error:
            return f"{os.path.basename(path)}: could not read the spec to check its status ({error})."
    old = status_of(before) if before is not None else None
    name = os.path.basename(path)
    after = after_edit(payload.get("tool_name"), tool_input, before)
    if after is None:
        if old in STATUSES:
            return (
                f"{name}: could not match this edit against the spec exactly, so its status rules "
                "cannot be checked. Read the file again and copy old_string from it exactly."
            )
        return None

    new = status_of(after)
    if old not in STATUSES and new not in STATUSES:
        return None
    if sum(line.startswith("status:") for line in frontmatter(after) or []) > 1:
        return f"{name}: the frontmatter has more than one `status:` line; keep one."
    if new not in STATUSES:
        found = f"'{new}'" if new else "none"
        return (
            f"{name}: the spec needs `status:` frontmatter set to Draft, Ready to build or Built "
            f"(found {found})."
        )
    if old not in STATUSES and new != "Draft":
        return (
            f"{name}: a new spec must be written as Draft, not {new}. If you are moving an "
            "existing spec, move it with `git mv`, which keeps its status."
        )
    if new == old:
        if new != "Draft" and without_status(after) != without_status(before):
            return (
                f"{name}: this spec is {old}, so changing it must also set its status back to "
                "Draft, because what was agreed or built no longer matches."
            )
        return None
    if new == "Built":
        return (
            f"{name}: only the build step sets Built, once its review finds every requirement "
            "verified. Leave the status as it is."
        )
    if old in ("Ready to build", "Built") and new != "Draft":
        return f"{name}: a {old} spec can only go back to Draft, not to {new}."
    if new == "Ready to build" and has_open_questions(after):
        return (
            f"{name}: it still has open questions, so it cannot be Ready to build. Answer them "
            "with the person, or leave the spec as Draft."
        )
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Input: the PreToolUse hook JSON on stdin. Output: nothing when allowed; the reason "
            "on stderr when refused. Exit codes: 0 allows the edit (including when the input "
            "cannot be read); 2 refuses it, and Claude Code shows Claude the reason."
        ),
    )
    parser.parse_args(argv)
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    reason = check(payload) if isinstance(payload, dict) else None
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
