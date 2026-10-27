#!/usr/bin/env python3
"""Refuse spec and ADR status changes the lifecycle does not allow.

Claude Code runs this as a PreToolUse hook on Write, Edit and MultiEdit. It reads the hook's
JSON from stdin and, for a *.spec.md under the project's docs/specs/ or a *.md directly under
its docs/adrs/ (the project being $CLAUDE_PROJECT_DIR, or the current directory if unset),
works out what the file would contain after the edit and compares it with what is on disk now.
For a spec it refuses:

- a spec that had a lifecycle status (Draft, Ready to build or Built) losing it;
- a spec that had none being given any status but Draft, so new specs start as Draft;
- setting Built: only the build step may, and it does not exist yet;
- Ready to build or Built to anything but Draft;
- Ready to build while the Open questions section is not empty or "None.", or in the same edit
  as any other change;
- a change to a Ready to build or Built spec that does not return it to Draft.

For an ADR (architecture decision record) it refuses:

- an ADR that had a status (Draft, Accepted, Rejected or Superseded) losing it;
- a new ADR with any status but Draft;
- Accepted or Rejected, except from Draft and as an edit that changes nothing else;
- Superseded, except from Accepted with a `superseded-by:` line added and nothing else changed;
- any other change to an Accepted, Rejected or Superseded ADR, since a decided ADR is never
  edited, only superseded by a new one.

Whether a person really accepted an ADR is beyond a hook; the skill asks them.

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
ADR_STATUSES = ("Draft", "Accepted", "Rejected", "Superseded")
EMPTY_ANSWERS = {"", "none", "none."}
FOOTNOTE = re.compile(r"^\[[^\]]+\]:")


def project_parts(path):
    """The path's parts relative to the project ($CLAUDE_PROJECT_DIR or cwd)."""
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    relative = os.path.relpath(os.path.abspath(path), os.path.abspath(project))
    return os.path.normpath(relative).split(os.sep)


def is_spec(path):
    """True for a *.spec.md under docs/specs/ in the project."""
    parts = project_parts(path)
    return parts[:2] == ["docs", "specs"] and parts[-1].endswith(".spec.md")


def is_adr(path):
    """True for a *.md directly under docs/adrs/ in the project."""
    parts = project_parts(path)
    return len(parts) == 3 and parts[:2] == ["docs", "adrs"] and parts[-1].endswith(".md")


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


def without_status(text, also=()):
    """The text's lines without its frontmatter status line, nor any line starting with `also`."""
    lines = text.lstrip("\ufeff").splitlines()
    end = len(frontmatter(text) or []) + 1
    keys = ("status:",) + tuple(also)
    return [line for i, line in enumerate(lines) if i > end or not line.startswith(keys)]


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
    if not path:
        return None
    if is_spec(path):
        kind, statuses, rules = "spec", STATUSES, spec_rules
    elif is_adr(path):
        kind, statuses, rules = "ADR", ADR_STATUSES, adr_rules
    else:
        return None
    before = None
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                before = f.read()
        except (OSError, UnicodeDecodeError) as error:
            return f"{os.path.basename(path)}: could not read the {kind} to check its status ({error})."
    old = status_of(before) if before is not None else None
    name = os.path.basename(path)
    after = after_edit(payload.get("tool_name"), tool_input, before)
    if after is None:
        if old in statuses:
            return (
                f"{name}: could not match this edit against the {kind} exactly, so its status rules "
                "cannot be checked. Read the file again and copy old_string from it exactly."
            )
        return None
    return rules(name, before, after, old)


def spec_rules(name, before, after, old):
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
    if new == "Ready to build" and without_status(after) != without_status(before or ""):
        return (
            f"{name}: set Ready to build on its own, as the last edit after a passing review; "
            "this edit also changes the spec's content."
        )
    if new == "Ready to build" and has_open_questions(after):
        return (
            f"{name}: it still has open questions, so it cannot be Ready to build. Answer them "
            "with the person, or leave the spec as Draft."
        )
    return None


def adr_rules(name, before, after, old):
    new = status_of(after)
    if old not in ADR_STATUSES and new not in ADR_STATUSES:
        return None
    if sum(line.startswith("status:") for line in frontmatter(after) or []) > 1:
        return f"{name}: the frontmatter has more than one `status:` line; keep one."
    if new not in ADR_STATUSES:
        found = f"'{new}'" if new else "none"
        return (
            f"{name}: the ADR needs `status:` frontmatter set to Draft, Accepted, Rejected or "
            f"Superseded (found {found})."
        )
    if old not in ADR_STATUSES and new != "Draft":
        return (
            f"{name}: a new ADR must be written as Draft, not {new}. Only the person accepts or "
            "rejects a decision, once they have seen it reviewed."
        )
    if old not in ADR_STATUSES:
        return None
    if new == old:
        if new != "Draft" and without_status(after) != without_status(before):
            return (
                f"{name}: this ADR is {old}, and a decided ADR is never edited. To change the "
                "decision, write a new Draft ADR that supersedes it."
            )
        return None
    if old == "Draft" and new in ("Accepted", "Rejected"):
        if without_status(after) != without_status(before):
            return (
                f"{name}: set {new} on its own, as the last edit after a passing review and the "
                "person's sign-off; this edit also changes the ADR's content."
            )
        return None
    if old == "Accepted" and new == "Superseded":
        added = [line for line in frontmatter(after) or [] if line.startswith("superseded-by:")]
        had = [line for line in frontmatter(before) or [] if line.startswith("superseded-by:")]
        if len(added) != 1 or had or not added[0][len("superseded-by:"):].strip():
            return (
                f"{name}: setting Superseded must add one `superseded-by:` line naming the number "
                "of the ADR that replaces it."
            )
        if without_status(after, also=("superseded-by:",)) != without_status(before):
            return (
                f"{name}: setting Superseded may only change the status and add `superseded-by:`; "
                "the rest of a decided ADR is never edited."
            )
        return None
    return (
        f"{name}: an ADR cannot go from {old} to {new}. Draft becomes Accepted or Rejected; "
        "Accepted becomes Superseded; nothing else changes."
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
