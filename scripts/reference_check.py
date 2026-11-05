#!/usr/bin/env python3
"""Refuse a brief, spec or ADR that refers to material outside the lifecycle's own documents.

Claude Code runs this as a PreToolUse hook on Write, Edit and MultiEdit, from status_check.sh.
It reads the hook's JSON from stdin and, for the project's docs/brief.md, a *.spec.md under its
docs/specs/ or a *.md under its docs/adrs/ (the project being $CLAUDE_PROJECT_DIR, or the
current directory if unset), works out what the file would contain after the edit. It reads every
inline link and image, `[text](target)`, and every reference definition, `[name]: target`,
outside code spans and fenced code blocks, and refuses the edit if any target is:

- a web address with a scheme other than `http`, `https` or `mailto`, such as `file:`;
- an absolute path, or one starting `~`;
- a relative path that leaves the project;
- a relative path to a file under docs/ that is not a lifecycle document: the brief, a spec, an
  ADR, a plan or a spike record.

These documents stand on their own: what matters from material they were drafted from is stated
in their own words, and outside material is referred to only by a web link. Any other target,
such as a path to code or a `#heading` of the same document, is not checked; which lifecycle
documents may refer to which is left to the reviewers, as are references by title or by a path
written as plain text. A document that already holds such a reference is refused on its next
edit until the reference is removed. An edit that can't be matched against the file is left to
status_check.py, which runs first.
"""

import argparse
import json
import os
import sys
from urllib.parse import unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import doc_references  # noqa: E402
import status_check  # noqa: E402

WEB = ("http", "https", "mailto")


def is_brief(path):
    """True for docs/brief.md in the project, whatever the case."""
    return [part.lower() for part in status_check.project_parts(path)] == ["docs", "brief.md"]


def is_lifecycle_document(path):
    return (is_brief(path) or status_check.is_spec(path) or status_check.is_adr(path)
            or status_check.is_plan(path) or status_check.is_spike(path))


def problem(source, target):
    """Why the target may not be referred to, or None if it may."""
    path = target.partition("#")[0]
    if not path:
        return None
    scheme = doc_references.SCHEME.match(path)
    if scheme:
        if scheme.group(0)[:-1].lower() in WEB:
            return None
        return "is not a web link"
    path = unquote(path)
    if path.startswith(("/", "~", "\\")):
        return "is outside the repository"
    full = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(source)), path))
    parts = status_check.project_parts(full)
    if parts[0] == os.pardir:
        return "is outside the repository"
    if parts[0].lower() == "docs" and not is_lifecycle_document(full):
        return "is a file under docs/ that is not a lifecycle document"
    return None


def check(payload):
    """Return the reason to refuse the tool call, or None to allow it."""
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path", "")
    if not path:
        return None
    if is_brief(path):
        kind = "brief"
    elif status_check.is_spec(path):
        kind = "spec"
    elif status_check.is_adr(path):
        kind = "ADR"
    else:
        return None
    before = None
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                before = f.read()
        except (OSError, UnicodeDecodeError):
            return None
    after = status_check.after_edit(payload.get("tool_name"), tool_input, before)
    if after is None:
        return None
    found = []
    for _, line in doc_references.prose_lines(after):
        for target in doc_references.targets(line):
            wrong = problem(path, target)
            if wrong:
                found.append(f"- `{target}` {wrong}")
    if not found:
        return None
    return (
        f"{os.path.basename(path)}: the {kind} stands on its own, so it refers to outside material "
        "only by a web link. Material handed over in the conversation, kept outside the repository "
        "or under docs/ beside the lifecycle's documents can change or vanish without the "
        f"{kind} being touched. State what matters from it in the {kind}'s own words, remove "
        "these references and tell the person why:\n" + "\n".join(found)
    )


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
