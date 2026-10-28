#!/usr/bin/env python3
"""Refuse spec and ADR status changes the lifecycle does not allow.

Claude Code runs this as a PreToolUse hook on Write, Edit and MultiEdit. It reads the hook's
JSON from stdin and, for a *.spec.md under the project's docs/specs/ or a *.md under its
docs/adrs/ (the project being $CLAUDE_PROJECT_DIR, or the current directory if unset),
works out what the file would contain after the edit and compares it with what is on disk now.
Every status carries its emoji, emoji first: a spec is `📝 Draft`, `🟢 Ready to build` or
`✅ Built`; an ADR is `📝 Draft`, `👍 Accepted`, `❌ Rejected` or `↪️ Superseded`. The U+FE0F that
some keyboards add after an emoji is optional. It refuses a status written by its word alone or
with the wrong emoji, and names the value to write. A document written before the emoji, whose
status is a bare word such as `Accepted`, counts as having that status, and an edit that only adds
the emoji to its status line is allowed, even on a decided ADR. Any other edit to it must add the
emoji too.

For a spec it refuses:

- a spec that had a lifecycle status losing it;
- a spec that had none being given any status but `📝 Draft`, so new specs start as Draft;
- setting `✅ Built`: only the build step may, and it does not exist yet;
- `🟢 Ready to build` or `✅ Built` to anything but `📝 Draft`;
- `🟢 Ready to build` while the Open questions section is not empty or "None.", or in the same
  edit as any other change;
- a change to a `🟢 Ready to build` or `✅ Built` spec that does not return it to `📝 Draft`.

For an ADR (architecture decision record) it refuses:

- an ADR that had a status losing it;
- a new ADR with any status but `📝 Draft`, including one the lifecycle does not know;
- `👍 Accepted` or `❌ Rejected`, except from `📝 Draft` and as an edit that changes nothing else;
- `↪️ Superseded`, except from `👍 Accepted` with a `superseded-by:` line added and nothing else
  changed, naming the four-digit number of a `👍 Accepted` ADR in the same folder whose
  `supersedes:` names this one (it may name several);
- any other change to a `👍 Accepted`, `❌ Rejected` or `↪️ Superseded` ADR, since a decided ADR
  is never edited, only superseded by a new one.

Whether a person really accepted an ADR is beyond a hook; the skill asks them.

A file that has no lifecycle status before or after the edit, nor one named by its word, is left
alone, so a project that keeps other files under docs/specs/ or docs/adrs/ is not affected; only a
new ADR with a status the lifecycle does not know is refused. Edits made any other way, by hand or through
a shell command, are not seen.
"""

import argparse
import json
import os
import re
import sys

DRAFT, READY, BUILT = "📝 Draft", "🟢 Ready to build", "✅ Built"
ACCEPTED, REJECTED, SUPERSEDED = "👍 Accepted", "❌ Rejected", "↪️ Superseded"
STATUSES = (DRAFT, READY, BUILT)
ADR_STATUSES = (DRAFT, ACCEPTED, REJECTED, SUPERSEDED)
# Each status by its word alone, as documents written before the emoji hold it.
WORDS = {value.split(" ", 1)[1]: value for value in STATUSES + ADR_STATUSES}
# U+FE0F asks for an emoji to be drawn in colour; some keyboards add it and some don't.
VARIATION = "\ufe0f"
WITHOUT_VARIATION = {value.replace(VARIATION, ""): value for value in WORDS.values()}
NEW_HINT = {
    "spec": "If you are moving an existing spec, move it with `git mv`, which keeps its status.",
    "ADR": "Only the person accepts or rejects a decision, once they have seen it reviewed.",
}
EMPTY_ANSWERS = {"", "none", "none."}
FOOTNOTE = re.compile(r"^\[[^\]]+\]:")


def project_parts(path):
    """The path's parts relative to the project ($CLAUDE_PROJECT_DIR or cwd)."""
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    relative = os.path.relpath(os.path.abspath(path), os.path.abspath(project))
    return os.path.normpath(relative).split(os.sep)


def is_spec(path):
    """True for a *.spec.md under docs/specs/ in the project, whatever the folders' case."""
    parts = project_parts(path)
    return [part.lower() for part in parts[:2]] == ["docs", "specs"] and parts[-1].lower().endswith(".spec.md")


def is_adr(path):
    """True for a *.md anywhere under docs/adrs/ in the project, whatever the folders' case."""
    parts = project_parts(path)
    return [part.lower() for part in parts[:2]] == ["docs", "adrs"] and parts[-1].lower().endswith(".md")


def frontmatter(text):
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for end, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:end]
    return None


def is_key(line, *keys):
    """True if the frontmatter line sets one of the keys, in any case, as `key:` or `key :`."""
    return any(re.match(rf"{re.escape(key)}\s*:", line, re.IGNORECASE) for key in keys)


def field(text, key):
    """The value of a frontmatter key, without comment or quotes."""
    for line in frontmatter(text) or []:
        if is_key(line, key):
            value = line.split(":", 1)[1].split("#", 1)[0].strip()
            return value.strip("\"'")
    return None


def comment(text, key):
    """The comment after a frontmatter key's value, if any."""
    for line in frontmatter(text) or []:
        if is_key(line, key):
            parts = line.split(":", 1)[1].split("#", 1)
            return parts[1].strip() if len(parts) > 1 else None
    return None


def status_of(text):
    """The frontmatter status, read the same with or without U+FE0F after its emoji."""
    value = field(text, "status")
    if value is None:
        return None
    return WITHOUT_VARIATION.get(value.replace(VARIATION, ""), value)


def lifecycle_status(text):
    """The status, counting a bare word such as `Accepted` from before the emoji as its full value."""
    value = status_of(text)
    return WORDS.get(value, value)


def meant(value, allowed):
    """The full status in `allowed` that `value` names by its word, as `Draft` or `🟢 Built` do."""
    full = WORDS.get(re.sub(r"^[^A-Za-z]*", "", value or ""))
    return full if full in allowed else None


def moving_over(before, after):
    """True if the edit only gives a status written before the emoji its emoji.

    The status line may change its quotes and spacing too, but not its comment.
    """
    word = field(before, "status")
    return (
        word in WORDS
        and status_of(after) == WORDS[word]
        and comment(before, "status") == comment(after, "status")
        and without_status(after) == without_status(before)
    )


def listed(values):
    named = [f"`{value}`" for value in values]
    return ", ".join(named[:-1]) + " or " + named[-1]


def without_status(text, also=()):
    """The text's lines without its frontmatter status line, nor any line setting a key in `also`."""
    lines = text.lstrip("\ufeff").splitlines()
    end = len(frontmatter(text) or []) + 1
    return [line for i, line in enumerate(lines) if i > end or not is_key(line, "status", *also)]


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
    old = lifecycle_status(before) if before is not None else None
    name = os.path.basename(path)
    after = after_edit(payload.get("tool_name"), tool_input, before)
    if after is None:
        if old in statuses:
            return (
                f"{name}: could not match this edit against the {kind} exactly, so its status rules "
                "cannot be checked. Read the file again and copy old_string from it exactly."
            )
        return None

    written = status_of(after)
    new = written if written in statuses else meant(written, statuses) or written
    # A status missing its emoji is judged as the one it names first, so a move the lifecycle
    # refuses anyway is refused for that, not with advice that only leads to that refusal.
    reason = lifecycle_problem(path, kind, statuses, rules, before, after, old, new)
    if reason or new == written:
        return reason
    return (
        f"{name}: write the status with its emoji, as `{new}` (found '{written}'). The {kind} "
        f"statuses are {listed(statuses)}."
    )


def lifecycle_problem(path, kind, statuses, rules, before, after, old, new):
    name = os.path.basename(path)
    if old not in statuses and new not in statuses:
        if kind == "ADR" and not before and new is not None:
            return f"{name}: a new ADR must be written as `{DRAFT}`, not '{new}'."
        return None
    if sum(is_key(line, "status") for line in frontmatter(after) or []) > 1:
        return f"{name}: the frontmatter has more than one `status:` line; keep one."
    if new not in statuses:
        found = f"'{new}'" if new else "none"
        return f"{name}: the {kind} needs `status:` frontmatter set to {listed(statuses)} (found {found})."
    if old not in statuses and new != DRAFT:
        if old:
            return f"{name}: '{old}' is not a lifecycle status; set the {kind} to `{DRAFT}` first."
        return f"{name}: a new {kind} must be written as `{DRAFT}`, not `{new}`. {NEW_HINT[kind]}"
    return rules(path, before, after, old, new)


def spec_rules(path, before, after, old, new):
    name = os.path.basename(path)
    if old not in STATUSES:
        return None
    if new == old:
        if new != DRAFT and without_status(after) != without_status(before):
            return (
                f"{name}: this spec is `{old}`, so changing it must also set its status back to "
                f"`{DRAFT}`, because what was agreed or built no longer matches."
            )
        return None
    if new == BUILT:
        return (
            f"{name}: only the build step sets `{BUILT}`, once its review finds every requirement "
            "verified. Leave the status as it is."
        )
    if old in (READY, BUILT) and new != DRAFT:
        return f"{name}: a `{old}` spec can only go back to `{DRAFT}`, not to `{new}`."
    if new == READY and without_status(after) != without_status(before or ""):
        return (
            f"{name}: set `{READY}` on its own, as the last edit after a passing review; "
            "this edit also changes the spec's content."
        )
    if new == READY and has_open_questions(after):
        return (
            f"{name}: it still has open questions, so it cannot be `{READY}`. Answer them "
            f"with the person, or leave the spec as `{DRAFT}`."
        )
    return None


def replacement_problem(path, number):
    """Why the ADR numbered `number` cannot supersede the ADR at `path`, or None if it can."""
    own = re.match(r"\d{4}(?=-)", os.path.basename(path))
    if not own:
        return "its file name does not start with its four-digit number"
    if number == own.group():
        return "an ADR cannot supersede itself"
    folder = os.path.dirname(os.path.abspath(path))
    matches = [n for n in sorted(os.listdir(folder)) if n.startswith(number + "-") and n.lower().endswith(".md")]
    if not matches:
        return f"there is no ADR {number} in this folder"
    if len(matches) > 1:
        return f"more than one ADR is numbered {number}; renumber one first"
    try:
        with open(os.path.join(folder, matches[0]), encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as error:
        return f"ADR {number} could not be read ({error})"
    if lifecycle_status(text) != ACCEPTED:
        return (
            f"ADR {number} is not `{ACCEPTED}` yet; the old ADR stays `{ACCEPTED}` until the "
            "person accepts it"
        )
    if own.group() not in re.findall(r"\d{4}", field(text, "supersedes") or ""):
        return f"ADR {number} does not name this ADR in its `supersedes:` line"
    return None


def adr_rules(path, before, after, old, new):
    name = os.path.basename(path)
    if old not in ADR_STATUSES:
        return None
    if new == old:
        if new != DRAFT and after != before and not moving_over(before, after):
            return (
                f"{name}: this ADR is `{old}`, and a decided ADR is never edited. To change the "
                f"decision, write a new `{DRAFT}` ADR that supersedes it."
            )
        return None
    if old == DRAFT and new in (ACCEPTED, REJECTED):
        if without_status(after) != without_status(before):
            return (
                f"{name}: set `{new}` on its own, as the last edit after a passing review and the "
                "person's sign-off; this edit also changes the ADR's content."
            )
        return None
    if old == ACCEPTED and new == SUPERSEDED:
        added = [line for line in frontmatter(after) or [] if is_key(line, "superseded-by")]
        if len(added) != 1 or field(before, "superseded-by") is not None:
            return (
                f"{name}: setting `{SUPERSEDED}` must add one `superseded-by:` line naming the "
                "four-digit number of the ADR that replaces it."
            )
        number = field(after, "superseded-by")
        if not re.fullmatch(r"\d{4}", number or ""):
            return f"{name}: `superseded-by:` must be the four-digit number of the replacing ADR."
        problem = replacement_problem(path, number)
        if problem:
            return f"{name}: cannot set `{SUPERSEDED}`: {problem}."
        if without_status(after, also=("superseded-by",)) != without_status(before):
            return (
                f"{name}: setting `{SUPERSEDED}` may only change the status and add `superseded-by:`; "
                "the rest of a decided ADR is never edited."
            )
        return None
    return (
        f"{name}: an ADR cannot go from `{old}` to `{new}`. `{DRAFT}` becomes `{ACCEPTED}` or "
        f"`{REJECTED}`; `{ACCEPTED}` becomes `{SUPERSEDED}`; nothing else changes."
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
