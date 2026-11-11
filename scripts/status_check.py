#!/usr/bin/env python3
"""Refuse spec, ADR, plan and spike record status changes the lifecycle does not allow, a
lifecycle document whose `type:` is wrong, and open questions not laid out as ADR 0030 says.

Claude Code runs this as a PreToolUse hook on Write, Edit and MultiEdit. It reads the hook's
JSON from stdin and, for the project's docs/brief.md, a *.spec.md under its docs/specs/, a *.md
under its docs/adrs/ or a *.md directly in its docs/plans/ or docs/spikes/ (the project being
$CLAUDE_PROJECT_DIR, or the current directory if unset),
works out what the file would contain after the edit and compares it with what is on disk now.
Every status carries its emoji, emoji first: a spec is `📝 Draft` or `👍 Accepted`, describing the
document, never the software; a plan is `📝 Draft`, `🟢 Ready to build` or `✅ Built`; an ADR is `📝 Draft`, `👍 Accepted`, `❌ Rejected` or `↪️ Superseded`; a spike record is `📝 Draft`, `🟢 Ready to run`, `💡 Confirmed`, `🚫 Refuted` or `❔ Not settled`. The U+FE0F that
some keyboards add after an emoji is optional. It refuses a status written by its word alone or
with the wrong emoji, and names the value to write. A document written before the emoji, whose
status is a bare word such as `Accepted`, counts as having that status, and an edit that only adds
the emoji to its status line is allowed, even on a decided ADR. Any other edit to it must add the
emoji too.

For a spec it refuses:

- a spec that had a lifecycle status losing it;
- a spec that had none being given any status but `📝 Draft`, so new specs start as Draft;
- `👍 Accepted` while the Open questions section is missing or holds anything but "None.", or in
  the same edit as any other change;
- a change to a `👍 Accepted` spec that does not return it to `📝 Draft`;
- `👍 Accepted` for a spec still heading a requirement `### Requirement: <name>`, as specs written
  for an earlier version of the plugin did, until it is reworked with /spec.

A spec still holding `🟢 Ready to build` or `✅ Built`, statuses specs had before, is no longer
checked until it is set back to `📝 Draft`, which is allowed; setting it to `👍 Accepted` straight
away is refused.

For an ADR (architecture decision record) it refuses:

- an ADR that had a status losing it;
- a new ADR with any status but `📝 Draft`, including one the lifecycle does not know;
- `👍 Accepted` or `❌ Rejected`, except from `📝 Draft` and as an edit that changes nothing else;
- `👍 Accepted` while the Open questions section is missing, or holds anything but "None.", while
  the Decision section does not open with "Chosen:" and the option, or while the ADR's plain part,
  everything between the frontmatter and `## Technical detail` apart from HTML comments, holds more
  than 500 words, counted as for a spike record; a draft in the layout from before those
  sections is told to re-lay it first;
- `↪️ Superseded`, except from `👍 Accepted` with a `superseded-by:` line added and nothing else
  changed, naming the four-digit number of a `👍 Accepted` ADR in the same folder whose
  `supersedes:` names this one (it may name several);
- any other change to a `👍 Accepted`, `❌ Rejected` or `↪️ Superseded` ADR, since a decided ADR
  is never edited, only superseded by a new one.

For a plan it refuses:

- a plan that had a lifecycle status losing it, and a new plan with any status but `📝 Draft`;
- setting `✅ Built`: only `/build`'s hand-over script may, writing the file itself, so this hook
  never sees it;
- any change to a `✅ Built` plan, which is frozen once built (it may be deleted), apart from adding
  the emoji to its status line;
- `🟢 Ready to build` to anything but `📝 Draft`;
- `🟢 Ready to build` in the same edit as any other change, or while the Open questions section is
  missing or not empty or "None.";
- `🟢 Ready to build` unless the plan names something to build, each spec listed under Specs
  exists, is `👍 Accepted` and has a numbered heading under `## Requirements`, as
  `### 2. <name>`, for each requirement link beneath it, `  - [<name>](<path>#<anchor>)`, whose text
  gives the name alone and whose anchor is the one GitHub gives that heading; each ADR listed in
  the ADRs table, `| [<NNNN>](<path>) | <title> |`, exists, is `👍 Accepted`, shows its own number
  and is given by its title, word for word; a plan in the layout from before 0.38.0, with
  `- Requirement: <name>` lines or ADRs as bullets, is refused with a message saying how to
  rewrite it; and no
  other plan in the folder that is not `✅ Built` names the same requirement of the same spec. A
  spec still heading its requirements `### Requirement: <name>` is refused with a message saying it
  was written for an earlier version of the plugin and needs reworking with /spec. References are
  paths relative to the plan;
- a change to a `🟢 Ready to build` plan that does not return it to `📝 Draft`.

For a spike record it refuses:

- a record that had a lifecycle status losing it, and a new record with any status but `📝 Draft`
  or with anything in its Runs section;
- any change to the Runs section, at any status: only the run script (skills/spike/scripts/spike.py)
  writes runs, writing the file itself, so this hook never sees it;
- any move but `📝 Draft` to `🟢 Ready to run`, `🟢 Ready to run` back to `📝 Draft` while Runs is
  empty, and `🟢 Ready to run` to `💡 Confirmed`, `🚫 Refuted` or `❔ Not settled`;
- a move forward in the same edit as any other change, while the Open questions section is
  missing or not empty or "None.", or while the record's plain part, everything between the
  frontmatter and `## Experiment` apart from HTML comments, holds more than 600 words (counted as
  runs of non-space characters holding a letter or digit, so a table's bars and rules don't
  count); `💡 Confirmed` or `🚫 Refuted` while Runs holds no run; and a finishing status that the
  Finding does not open with, such as `💡 Confirmed` for a Finding that opens "Refuted:";
- a change to the Hypothesis, How we'll know, Out of scope, How the test works, Risks and
  safeguards or Experiment section of a `🟢 Ready to run` record that does not return it to
  `📝 Draft`;
- any change to a `💡 Confirmed`, `🚫 Refuted` or `❔ Not settled` record, which is final, apart
  from adding its `type:`.
  Deleting it is not an edit, so it is never refused.

HTML comments in the Runs section outside its code fences do not count as runs.

Every lifecycle document names its kind in its frontmatter's `type:`: `Brief` for docs/brief.md,
`Spec`, `ADR`, `Plan` or `Spike`. For the brief and for any document above with a lifecycle status
before or after the edit, it refuses a `type:` that is not the one for the document's folder, more
than one `type:` line, a new document without `type:`, and taking a document's `type:` away. A
document written before types may be edited without one, and adding one never counts as a change,
so it may come with any edit the rules above allow, even to a decided ADR, a `✅ Built` plan or a
finished spike record, whose only allowed change it is.

Every spec, ADR, plan and spike record records in its frontmatter's `date:` the day its status
last changed, as YYYY-MM-DD. For any of them with a lifecycle status before or after the edit, it
refuses more than one `date:` line, a date that is not a real YYYY-MM-DD date or is after today, a new document or a
status change whose `date:` is not today's date on this machine, and a change to `date:`, or
taking it away, while the status stays the same. A document written before dates may be edited
without one until its next status change, and adding one, any real date, never counts as a change,
so it may come with any edit the rules above allow, even to a decided ADR, a `✅ Built` plan or a
finished spike record. A rule that a status be set on its own lets the `date:` line change with it.

Every open question in the brief, a spec, an ADR, a plan or a spike record is laid out as ADR 0030
says: a heading `### N. <what is to be settled>`, numbered from 1 in order, then at least one line of
context, then one block quote, last in the entry, holding exactly one line starting
`> **Proposed:**` and, after it, exactly one line starting `> **Why:**`; or the section says only
"None.". HTML comments, footnote definitions and a closing horizontal rule in the section are
ignored, and a heading or `>` inside a fenced code block is text. A block quote earlier in the entry
counts as context; a quote runs on over its lines without `>`, as Markdown's lazy continuation lines
do, until a blank line. For the brief and for any document above with a lifecycle status before
or after the edit, it refuses an edit that adds the Open questions section or changes what it says,
apart from comments, footnotes and blank lines, while any entry breaks the layout, naming the entry and what is wrong. A document written before the layout
may be edited elsewhere as before; the first edit to its Open questions lays them all out again.

Whether a person really accepted an ADR or signed off a plan is beyond a hook; the skill asks them.

Apart from the brief, a file that has no lifecycle status before or after the edit, nor one named
by its word, is left alone, so a project that keeps other files under docs/specs/, docs/adrs/ or docs/plans/ is not affected; only a
new ADR with a status the lifecycle does not know is refused. Edits made any other way, by hand or through
a shell command, are not seen.
"""

import argparse
import datetime
import json
import os
import re
import sys
import unicodedata

DRAFT, READY, BUILT = "📝 Draft", "🟢 Ready to build", "✅ Built"
READY_TO_RUN = "🟢 Ready to run"
CONFIRMED, REFUTED, NOT_SETTLED = "💡 Confirmed", "🚫 Refuted", "❔ Not settled"
SPIKE_STATUSES = (DRAFT, READY_TO_RUN, CONFIRMED, REFUTED, NOT_SETTLED)
FINISHED = (CONFIRMED, REFUTED, NOT_SETTLED)
# A spike record's design: fixed once it is signed off.
FIXED_PARTS = ("Hypothesis", "How we'll know", "Out of scope", "How the test works", "Risks and safeguards",
               "Experiment")
PLAIN_LIMIT = 600  # words in a spike record's plain part, the part written for people
ADR_PLAIN_LIMIT = 500  # words in an ADR's plain part, from the title down to Technical detail
ADR_DETAIL = "Technical detail"  # the heading that starts an ADR's technical part
ADR_DIAGRAMS = "Decision"  # the section whose diagrams the word limit leaves out
WORD = re.compile(r"\S*[^\W_]\S*")  # a run of non-space characters holding a letter or digit
ACCEPTED, REJECTED, SUPERSEDED = "👍 Accepted", "❌ Rejected", "↪️ Superseded"
STATUSES = (DRAFT, READY, BUILT)
SPEC_STATUSES = (DRAFT, ACCEPTED)
ADR_STATUSES = (DRAFT, ACCEPTED, REJECTED, SUPERSEDED)
# Each status by its word alone, as documents written before the emoji hold it.
WORDS = {value.split(" ", 1)[1]: value for value in STATUSES + ADR_STATUSES + SPIKE_STATUSES}
# U+FE0F asks for an emoji to be drawn in colour; some keyboards add it and some don't.
VARIATION = "\ufe0f"
WITHOUT_VARIATION = {value.replace(VARIATION, ""): value for value in WORDS.values()}
NEW_HINT = {
    "spec": "If you are moving an existing spec, move it with `git mv`, which keeps its status.",
    "ADR": "Only the person accepts or rejects a decision, once they have seen it reviewed.",
    "plan": f"Set `{READY}` on its own once the person signs the plan off.",
    "spike record": f"Set `{READY_TO_RUN}` on its own once the person signs the design off.",
}
EMPTY_ANSWERS = {"", "none", "none."}
FOOTNOTE = re.compile(r"^\[[^\]]+\]:")
LINK = re.compile(r"^- \[[^\]]*\]\(<?([^)>\s]+)>?\)")
# A plan names each requirement as a link to its heading, nested beneath its spec:
# `  - [Reply to all](../specs/mail.spec.md#2-reply-to-all)`.
REQUIREMENT_LINK = re.compile(r"^\s+- \[([^\]]+)\]\(<?([^)>\s#]*)(?:#([^)>\s]*))?>?\)(?:\[\^[^\]]+\])*\s*$")
# Plans written before 0.38.0 named each requirement as `  - Requirement: <name>`.
REQUIREMENT_LINE = re.compile(r"^\s+- Requirement:\s*(.+?)\s*$")
# A plan lists its ADRs as rows of a `| ADR | Decision |` table: `| [0003](../adrs/0003-x.md) | <title> |`.
ADR_ROW = re.compile(r"^\|\s*\[([^\]]*)\]\(<?([^)>\s]+)>?\)(?:\[\^[^\]]+\])*\s*\|\s*(.*?)\s*\|\s*$")
FOOTNOTE_MARK = re.compile(r"\[\^[^\]]+\]")
TABLE_HEADER = re.compile(r"^\|\s*ADR\s*\|\s*Decision\s*\|\s*$", re.I)
TABLE_RULE = re.compile(r"^\|[\s:|-]+\|\s*$")
SPEC_FORM = "`- [<spec title>](<path>)` with `  - [<requirement name>](<path>#<heading anchor>)` beneath it"
ADR_FORM = "rows of a `| ADR | Decision |` table, as `| [<NNNN>](<path>) | <the ADR's title> |`"
# A requirement is a numbered `###` heading inside `## Requirements`, as `### 2. Reply to all`;
# the number is for reading only, and a plan names the requirement by the rest.
REQUIREMENT_HEADING = re.compile(r"^###\s+\d+\.\s+(.+?)\s*$")
# Specs written before numbered requirements headed each one `### Requirement: <name>`.
OLD_REQUIREMENT_HEADING = re.compile(r"^###\s+Requirement:")
LEADING_NUMBER = re.compile(r"^\d+\s*[.)]?\s+")
OLD_LAYOUT = "was written for an earlier version of the agentic plugin; rework it with /spec"
# Each kind of document by the value its frontmatter's `type:` holds.
TYPES = {"brief": "Brief", "spec": "Spec", "ADR": "ADR", "plan": "Plan", "spike record": "Spike"}


def today():
    """Today's date on this machine, as YYYY-MM-DD: the date a status change must carry."""
    return datetime.date.today().isoformat()


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


def is_plan(path):
    """True for a *.md directly in docs/plans/ in the project, whatever the folders' case."""
    parts = project_parts(path)
    return (len(parts) == 3 and [part.lower() for part in parts[:2]] == ["docs", "plans"]
            and parts[-1].lower().endswith(".md"))


def is_brief(path):
    """True for the project's docs/brief.md, whatever the case."""
    return [part.lower() for part in project_parts(path)] == ["docs", "brief.md"]


def is_spike(path):
    """True for a *.md directly in docs/spikes/ in the project, whatever the folders' case."""
    parts = project_parts(path)
    return (len(parts) == 3 and [part.lower() for part in parts[:2]] == ["docs", "spikes"]
            and parts[-1].lower().endswith(".md"))


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


def entry(text, key):
    """A frontmatter key's (value without quotes, comment or None), or None if it has none."""
    for line in frontmatter(text) or []:
        if is_key(line, key):
            parts = line.split(":", 1)[1].split("#", 1)
            return parts[0].strip().strip("\"'"), parts[1].strip() if len(parts) > 1 else None
    return None


def field(text, key):
    """The value of a frontmatter key, without comment or quotes."""
    found = entry(text, key)
    return found[0] if found else None


def status_of(text):
    """The frontmatter status, read the same with or without U+FE0F after its emoji."""
    value = field(text, "status")
    if value is None:
        return None
    return WITHOUT_VARIATION.get(value.replace(VARIATION, ""), value)


def lifecycle_status(text, statuses):
    """The status as one of `statuses` if it names one, even without its emoji or with the wrong
    one, as a document written before the emoji does; otherwise the status as written."""
    return canonical(status_of(text), statuses)


def canonical(value, statuses):
    return value if value in statuses else meant(value, statuses) or value


def meant(value, allowed):
    """The full status in `allowed` that `value` names by its word, as `Draft` or `🟢 Built` do."""
    # Only a leading emoji is dropped, so `202 Accepted` or `- Draft` names no status.
    full = WORDS.get(re.sub(r"^[^\x00-\x7f]+ ?", "", value or ""))
    return full if full in allowed else None


def restyled(before, after):
    """True if the edit changes only how the status value is written, such as adding its emoji.

    Callers have already found the status the same before and after; its comment must not change.
    """
    return (
        (entry(before, "status") or (None, None))[1] == (entry(after, "status") or (None, None))[1]
        and without_status(after) == without_status(before)
    )


def listed(values):
    named = [f"`{value}`" for value in values]
    return ", ".join(named[:-1]) + " or " + named[-1]


def without_status(text, also=()):
    """The text's lines without its frontmatter status, type and date lines, nor any line setting a
    key in `also`. Leaving out `type:` lets a document from before types gain one with any edit, and
    leaving out `date:` lets a status be set on its own with its date; date_problem() checks dates."""
    lines = text.lstrip("\ufeff").splitlines()
    end = len(frontmatter(text) or []) + 1
    return [line for i, line in enumerate(lines) if i > end or not is_key(line, "status", "type", "date", *also)]


def has_open_questions_section(text):
    return any(line.strip().lower() == "## open questions" for line in text.splitlines())


def in_footnotes(lines):
    """For each line, True if it is part of a footnote definition. A footnote runs on over lines
    indented by four spaces or a tab, and blank lines between."""
    flags, in_footnote = [], False
    for line in lines:
        in_footnote = bool(FOOTNOTE.match(line)) or (in_footnote and (not line.strip() or line.startswith(("    ", "\t"))))
        flags.append(in_footnote)
    return flags


def says_none(line):
    """True if the line says only that nothing is open, such as "None." or "- None."."""
    return line.strip().lstrip("-*").strip().strip("_*").strip().lower() in EMPTY_ANSWERS


def has_open_questions(text):
    """True if the Open questions section is missing or holds anything but "None.".

    Footnote definitions, including their continuation lines, are not questions.
    """
    lines = section(text, "Open questions")
    if lines is None:
        return True
    return any(not footnote and not says_none(line) for line, footnote in zip(lines, in_footnotes(lines)))


OPEN_QUESTIONS_LAYOUT = (
    'Lay out each open question as a heading `### 1. <what is to be settled>`, numbered in order, '
    "then the context it needs, then one block quote, last in the entry, holding a line starting "
    "`> **Proposed:**` with the answer you would choose (or what would settle it) and, after it, a "
    'line starting `> **Why:**` with the reason; or write "None." if nothing is open.'
)
QUESTION_HEADING = re.compile(r"^ {0,3}###\s+(.*?)\s*$")
NUMBERED = re.compile(r"^(\d+)\.(?:\s+(.*))?$")
QUOTE = re.compile(r"^ {0,3}>")
THEMATIC_BREAK = re.compile(r"^ {0,3}([-*_])(?:\s*\1){2,}\s*$")
# A line that starts a new block, so it never continues a block quote lazily: a list item, a
# heading, a code fence or a horizontal rule.
STARTS_BLOCK = re.compile(r"^ {0,3}(?:[-*+](?:\s|$)|\d{1,9}[.)](?:\s|$)|#{1,6}(?:\s|$)|`{3,}|~{3,})")


def open_questions_entries(lines):
    """The Open questions lines, without HTML comments and footnote definitions, as (the text
    before the first heading, [(heading, [(line, fenced)])]); `fenced` marks a line in a fenced
    code block, where neither a heading nor a quote counts."""
    lines = uncommented(lines).splitlines()
    fenced, _ = scan(lines)
    before, entries = [], []
    for line, in_fence, footnote in zip(lines, fenced, in_footnotes(lines)):
        if footnote:
            continue
        heading = None if in_fence else QUESTION_HEADING.match(line)
        if heading:
            entries.append((heading.group(1), []))
        elif entries:
            entries[-1][1].append((line, in_fence))
        else:
            before.append(line)
    return before, entries


def quote_blocks(body):
    """The block quotes in an entry's body, each as its first and last index into the body's
    non-blank lines. A quote runs on over lines without `>` until a blank line, as Markdown's lazy
    continuation lines do, unless the line starts a block of its own, such as a list item; a line in
    a fenced code block is never part of one."""
    blocks, open_block, index = [], False, -1
    for line, in_fence in body:
        if not line.strip():
            open_block = False
            continue
        index += 1
        if not in_fence and QUOTE.match(line):
            if open_block:
                blocks[-1][1] = index
            else:
                blocks.append([index, index])
                open_block = True
        elif open_block and not in_fence and not STARTS_BLOCK.match(line) and not THEMATIC_BREAK.match(line):
            blocks[-1][1] = index
        else:
            open_block = False
    return blocks


def entry_problem(number, heading, body):
    """What is wrong with one open question's entry, or None."""
    numbered = NUMBERED.match(heading)
    if not numbered:
        return "its heading does not start with its number, as `### 1. <what is to be settled>`"
    if int(numbered.group(1)) != number:
        return f"its heading should have the number {number}, counting the entries in order"
    if not (numbered.group(2) or "").strip():
        return "its heading has no title after the number, saying what is to be settled"
    filled = [line for line, _ in body if line.strip()]
    while filled and THEMATIC_BREAK.match(filled[-1]):
        filled.pop()
    blocks = [block for block in quote_blocks(body) if block[0] < len(filled)]
    if not blocks:
        return "it has no block quote holding `> **Proposed:**` and `> **Why:**` lines"
    first, last = blocks[-1]
    if last != len(filled) - 1:
        return "its block quote must come last in the entry, with nothing after it"
    if first == 0:
        return "it has no context before its block quote"
    stripped = [QUOTE.sub("", line, count=1).strip() for line in filled]
    inside, outside = stripped[first:last + 1], stripped[:first]
    if any(line.startswith(("**Proposed:**", "**Why:**")) for line in outside):
        return ("its `> **Proposed:**` and `> **Why:**` lines must both be in its last block quote, "
                "after the context")
    proposed = [i for i, line in enumerate(inside) if line.startswith("**Proposed:**")]
    why = [i for i, line in enumerate(inside) if line.startswith("**Why:**")]
    if len(proposed) != 1:
        found = "no" if not proposed else str(len(proposed))
        return (f"its block quote holds {found} `> **Proposed:**` lines; keep exactly one `> **Proposed:**` "
                "line, and make a second proposal a question of its own")
    if len(why) != 1:
        found = "no" if not why else str(len(why))
        return f"its block quote holds {found} `> **Why:**` lines; keep exactly one `> **Why:**` line"
    if why[0] < proposed[0]:
        return "its `> **Why:**` line must come after its `> **Proposed:**` line"
    return None


def open_questions_problem(text, lines=None):
    """Why the text's Open questions section, or `lines` when given, is not in the layout of ADR
    0030, or None if it is, holds only "None.", or is missing (which the status rules judge)."""
    if lines is None:
        lines = section(text, "Open questions")
    if lines is None:
        return None
    before, entries = open_questions_entries(lines)
    stray = [line for line in before if line.strip()]
    if not entries:
        if all(says_none(line) for line in stray):
            return None
        return f'Open questions holds text that is not an entry under a heading. {OPEN_QUESTIONS_LAYOUT}'
    if stray:
        return (f'Open questions holds text before its first entry\'s heading, such as "{stray[0].strip()}". '
                f"{OPEN_QUESTIONS_LAYOUT}")
    for number, (heading, body) in enumerate(entries, 1):
        problem = entry_problem(number, heading, body)
        if problem:
            title = NUMBERED.match(heading)
            title = (title.group(2) or "").strip() if title else heading
            named = f' ("{title}")' if title else ""
            return f"Open questions entry {number}{named}: {problem}. {OPEN_QUESTIONS_LAYOUT}"
    return None


def questions_said(lines):
    """What the Open questions lines say, leaving out HTML comments, footnote definitions and
    blank lines, so an edit to those alone does not count as a change to the questions."""
    if lines is None:
        return None
    kept = uncommented(lines).splitlines()
    return [line.rstrip() for line, footnote in zip(kept, in_footnotes(kept)) if line.strip() and not footnote]


def layout_problem(name, before, after):
    """Why the edit is refused for its Open questions' layout: only when it adds them or changes
    what they say."""
    lines = section(after, "Open questions")
    if lines is None or questions_said(lines) == questions_said(section(before, "Open questions") if before else None):
        return None
    problem = open_questions_problem(after, lines)
    return f"{name}: {problem}" if problem else None


def open_questions_refusal(name, text, status, kind):
    if not has_open_questions_section(text):
        return (
            f"{name}: it has no Open questions section, so it cannot be `{status}`. Add the section "
            f'from the template, holding "None." if nothing is open, and have the {kind} reviewed '
            "again before the person signs it off."
        )
    return (
        f"{name}: it still has open questions, so it cannot be `{status}`. Answer them "
        f"with the person, or leave the {kind} as `{DRAFT}`."
    )


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


def count_key(text, key):
    """How many frontmatter lines set `key`."""
    return sum(is_key(line, key) for line in frontmatter(text) or [])


def article(kind):
    """The article that goes before a kind's name, as "an ADR" but "a spec"."""
    return "an" if kind == "ADR" else "a"


def type_problem(name, kind, before, after):
    """Why the document's `type:` is wrong, or None. A new document must have one, and one it has
    is never taken away; a document from before types may go without until its skill adds it."""
    expected = TYPES[kind]
    if count_key(after, "type") > 1:
        return f"{name}: the frontmatter has more than one `type:` line; keep one, `type: {expected}`."
    value = field(after, "type")
    if value is None:
        if before and field(before, "type") is None:
            return None
        if before:
            return f"{name}: keep `type: {expected}` in the frontmatter; it says what the document is."
        return f"{name}: a new {kind} starts its frontmatter with `type: {expected}`; add it."
    if value != expected:
        return f"{name}: {article(kind)} {kind} in this folder has `type: {expected}` (found '{value}')."
    return None


def real_date(value):
    """True for a real calendar date written YYYY-MM-DD."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or ""):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def date_problem(name, kind, before, after, old, new):
    """Why the document's `date:` is wrong, or None. It is the day the status last changed: a new
    document and every status change carry today's date, and it never changes otherwise. A document
    from before dates may go without one until its next status change, and may gain any real date."""
    if count_key(after, "date") > 1:
        return f"{name}: the frontmatter has more than one `date:` line; keep one."
    value, earlier = field(after, "date"), field(before, "date") if before else None
    if value is not None and not real_date(value):
        return (f"{name}: `date:` must be a real date written YYYY-MM-DD, the day the {kind}'s status "
                f"last changed (found '{value}').")
    day = today()
    if value is not None and value > day:
        return (f"{name}: `date:` is {value}, after today, {day}; it is the day the {kind}'s status "
                "last changed, so it can't be later than today.")
    if old != new:
        if value == day:
            return None
        if not before or old is None:
            return (f"{name}: a new {kind} carries `date: {day}`, today's date, in its frontmatter, "
                    "under `status:`: the day its status was set.")
        return (f"{name}: set `date: {day}`, today's date, in the frontmatter in the same edit as this "
                f"status change; `date:` is the day the {kind}'s status last changed.")
    if earlier is None:
        return None
    if value is None:
        return f"{name}: keep `date: {earlier}` in the frontmatter; it is the day the {kind}'s status last changed."
    if value != earlier:
        return (f"{name}: `date:` changes only with a status change, since it is the day the {kind}'s "
                f"status last changed; keep `date: {earlier}`.")
    return None


def brief_problem(payload, path):
    """Why an edit to the brief is refused: only for its `type:`, as the brief has no status."""
    before = None
    if os.path.exists(path):
        before = read(path)
        if before is None:
            return f"{os.path.basename(path)}: could not read the brief to check its type."
    after = after_edit(payload.get("tool_name"), payload.get("tool_input") or {}, before)
    if after is None:
        return None
    name = os.path.basename(path)
    return type_problem(name, "brief", before, after) or layout_problem(name, before, after)


def check(payload):
    """Return the reason to refuse the tool call, or None to allow it."""
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path", "")
    if not path:
        return None
    if is_brief(path):
        return brief_problem(payload, path)
    if is_spec(path):
        kind, statuses, rules = "spec", SPEC_STATUSES, spec_rules
    elif is_adr(path):
        kind, statuses, rules = "ADR", ADR_STATUSES, adr_rules
    elif is_plan(path):
        kind, statuses, rules = "plan", STATUSES, plan_rules
    elif is_spike(path):
        kind, statuses, rules = "spike record", SPIKE_STATUSES, spike_rules
    else:
        return None
    before = None
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                before = f.read()
        except (OSError, UnicodeDecodeError) as error:
            return f"{os.path.basename(path)}: could not read the {kind} to check its status ({error})."
    old = lifecycle_status(before, statuses) if before is not None else None
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
    new = canonical(written, statuses)
    # A status missing its emoji is judged as the one it names first, so a move the lifecycle
    # refuses anyway is refused for that, not with advice that only leads to that refusal.
    reason = lifecycle_problem(path, kind, statuses, rules, before, after, old, new, written)
    if not reason and (old in statuses or new in statuses):
        reason = (type_problem(name, kind, before, after) or date_problem(name, kind, before, after, old, new)
                  or layout_problem(name, before, after))
    if reason or new == written:
        return reason
    return (
        f"{name}: write the status with its emoji, as `{new}` (found {written!r}). The {kind} "
        f"statuses are {listed(statuses)}."
    )


def lifecycle_problem(path, kind, statuses, rules, before, after, old, new, written):
    name = os.path.basename(path)
    if old not in statuses and new not in statuses:
        # A new document is refused any lifecycle status, even one only another kind uses, as
        # `✅ Built` on a spec; a new ADR is refused any status at all.
        if not before and new is not None and (kind == "ADR" or meant(new, WORDS.values())):
            return f"{name}: a new {kind} must be written as `{DRAFT}`, not '{new}'."
        return None
    if count_key(after, "status") > 1:
        return f"{name}: the frontmatter has more than one `status:` line; keep one."
    if new not in statuses:
        found = f"'{new}'" if new else "none"
        about = " A spec's status describes the document, not the software." if kind == "spec" else ""
        return f"{name}: the {kind} needs `status:` frontmatter set to {listed(statuses)} (found {found}).{about}"
    if old not in statuses and new != DRAFT:
        if old:
            return f"{name}: '{old}' is not a lifecycle status; set the {kind} to `{DRAFT}` first."
        return f"{name}: a new {kind} must be written as `{DRAFT}`, not '{written}'. {NEW_HINT[kind]}"
    return rules(path, before, after, old, new)


def spec_rules(path, before, after, old, new):
    name = os.path.basename(path)
    if old not in SPEC_STATUSES:
        return None
    if new == old:
        if new != DRAFT and without_status(after) != without_status(before):
            return (
                f"{name}: this spec is `{old}`, so changing it must also set its status back to "
                f"`{DRAFT}`, for the person to accept it again."
            )
        return None
    if new == ACCEPTED:
        if without_status(after) != without_status(before or ""):
            return (
                f"{name}: set `{ACCEPTED}` on its own, as the last edit after a passing review; "
                "this edit also changes the spec's content."
            )
        if has_open_questions(after):
            return open_questions_refusal(name, after, ACCEPTED, "spec")
        if old_layout(after):
            return (f"{name} {OLD_LAYOUT} before it is accepted: it still heads a requirement "
                    "`### Requirement: <name>`.")
        if not spec_requirements(after):
            return (f"{name}: a spec is accepted only with at least one requirement, a numbered "
                    "heading under `## Requirements`, as `### 1. <name>`.")
    return None


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def closes_fence(line, fence):
    """Whether `line` closes a block opened by `fence`: the same character, at least as long, nothing after."""
    match = FENCE.match(line)
    return bool(match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence)
                and not match.group(2).strip())


def scan(lines):
    """One pass over the original lines: (fenced, comments).

    fenced[i] is True for a fence line or a line inside a fenced code block. comments lists each
    HTML comment as ((line, column), (line, column after its `-->`)). A comment starts with `<!--`
    outside a fenced block and ends at the next `-->`, across lines and fences; a fence counts
    only at the start of a line outside a comment. A `<!--` with no `-->` after it is text, and so
    is everything after it. Nothing is read twice, so cutting a comment out can't make a new one.
    """
    fenced, comments = [False] * len(lines), []
    fence, opened, i, column, comments_possible = None, None, 0, 0, True
    while True:
        while i < len(lines):
            line = lines[i]
            if column == 0 and opened is None:
                if fence is not None:
                    fenced[i] = True
                    if closes_fence(line, fence):
                        fence = None
                    i += 1
                    continue
                match = FENCE.match(line)
                if match:
                    fence, fenced[i] = match.group(1), True
                    i += 1
                    continue
            mark = "-->" if opened else "<!--"
            found = line.find(mark, column) if comments_possible else -1
            if found < 0:
                i, column = i + 1, 0
            elif opened:
                comments.append((opened, (i, found + 3)))
                opened, column = None, found + 3
            else:
                opened, column = (i, found), found + 4
        if opened is None:
            return fenced, comments
        # Unclosed: read again from the line after it, as text with no comments.
        fence, i, column, comments_possible = None, opened[0] + 1, 0, False
        opened = None


def headings_allowed(lines):
    """For each line, False if it is a fence, inside a fenced code block or starts inside an HTML
    comment, where a heading is only text."""
    fenced, comments = scan(lines)
    return [not fenced[i] and not any(start < (i, 0) < end for start, end in comments) for i in range(len(lines))]


def section(text, heading):
    """The lines of the `## <heading>` section, or None if the text has none.

    A line inside a fenced code block, such as a run's output, never starts or ends a section.
    """
    lines = text.splitlines()
    allowed = headings_allowed(lines)
    starts = [i for i, line in enumerate(lines) if allowed[i] and line.strip().lower() == "## " + heading.lower()]
    if not starts:
        return None
    body = []
    for i in range(starts[0] + 1, len(lines)):
        if allowed[i] and (lines[i].startswith("# ") or lines[i].startswith("## ")):
            break
        body.append(lines[i])
    return body


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def target(plan_path, link):
    """The file a plan's reference points to, resolved from the plan's folder."""
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(plan_path)), link.split("#", 1)[0]))


def reference_lines(text, heading):
    """The non-blank lines of a plan's references section, without template comments or footnotes."""
    body = re.sub(r"<!--.*?-->", "", "\n".join(section(text, heading) or []), flags=re.S)
    lines = body.splitlines()
    return [line for line, footnote in zip(lines, in_footnotes(lines)) if line.strip() and not footnote]


def unreadable(line, heading):
    form = SPEC_FORM if heading == "Specs" else ADR_FORM
    return f"it cannot read the line '{line.strip()}' under {heading}; list them as {form}, or write \"None.\""


def named_specs(plan_path, text):
    """The plan's Specs section as ([(spec path, link as written, [(name, link target, anchor)])], problem).

    A link target is resolved from the plan's folder; the anchor is None when the link has none.
    """
    entries, problem = [], None
    for line in reference_lines(text, "Specs"):
        link = LINK.match(line)
        requirement = REQUIREMENT_LINK.match(line)
        if link and not line[:1].isspace():
            entries.append((target(plan_path, link.group(1)), link.group(1), []))
        elif requirement and entries:
            name, path, anchor = requirement.groups()
            entries[-1][2].append((name.strip(), target(plan_path, path) if path else None, anchor))
        elif REQUIREMENT_LINE.match(line) and entries:
            # Read on, so another plan's check for a shared requirement still sees this one.
            name = REQUIREMENT_LINE.match(line).group(1)
            entries[-1][2].append((name, None, None))
            problem = problem or (f"`- Requirement: {name}` is the layout plans had before; name each requirement as a "
                                  "link to its heading in the spec, as `  - [<requirement name>](<path>#<heading anchor>)`")
        elif line.strip().lstrip("-*").strip().lower() not in EMPTY_ANSWERS:
            return entries, problem or unreadable(line, "Specs")
    return entries, problem


def named_adrs(plan_path, text):
    """The plan's ADRs section as ([(ADR path, link as written, number as written, title as written)], problem)."""
    entries = []
    for line in reference_lines(text, "ADRs"):
        row = ADR_ROW.match(line)
        if TABLE_HEADER.match(line) or TABLE_RULE.match(line):
            continue
        if row:
            number, link, title = row.groups()
            entries.append((target(plan_path, link), link, number.strip(), FOOTNOTE_MARK.sub("", title).strip()))
        elif LINK.match(line):
            return entries, (f"'{line.strip()}' is the layout plans had before; list the ADRs as {ADR_FORM}")
        elif line.strip().lstrip("-*").strip().lower() not in EMPTY_ANSWERS:
            return entries, unreadable(line, "ADRs")
    return entries, None


def anchor_of(heading):
    """The anchor GitHub gives a heading's text: lowercased, with every character but letters, digits,
    underscores, hyphens and spaces dropped, and each space made a hyphen."""
    kept = (c for c in heading.strip().lower()
            if c in "_- " or unicodedata.category(c)[0] in "LNM")
    return "".join(kept).replace(" ", "-")


def title_of(text):
    """A document's `# ` title, after its frontmatter and outside code blocks and comments, or None."""
    lines = text.lstrip("\ufeff").splitlines()
    if frontmatter(text) is not None:
        lines = lines[len(frontmatter(text)) + 2:]
    for line in headings("\n".join(lines)):
        if line.startswith("# "):
            return line[2:].strip()
    return None


def requirements(plan_path, text):
    return {(spec, name) for spec, _, names in named_specs(plan_path, text)[0] for name, _, _ in names}


def headings(text):
    """The text's lines that can be headings: outside fenced code blocks and HTML comments."""
    lines = text.splitlines()
    return [line for line, allowed in zip(lines, headings_allowed(lines)) if allowed]


def spec_requirements(text):
    """The names of a spec's requirements, in order: its numbered headings under Requirements."""
    body = section(text, "Requirements") or []
    return [m.group(1) for m in map(REQUIREMENT_HEADING.match, headings("\n".join(body))) if m]


def spec_anchors(text):
    """{requirement name: the anchor GitHub gives its heading}, for a spec's numbered requirements."""
    body = section(text, "Requirements") or []
    found = {}
    for line in headings("\n".join(body)):
        m = REQUIREMENT_HEADING.match(line)
        if m:
            found[m.group(1)] = anchor_of(line.lstrip("#"))
    return found


def old_layout(text):
    """True if the spec heads a requirement `### Requirement: <name>`, as before numbering."""
    return any(OLD_REQUIREMENT_HEADING.match(line) for line in headings(text))


def old_layout_problem(link):
    return f"the spec {link} {OLD_LAYOUT}, accept it again, then sign the plan off again"


def described(status):
    return f"is '{status}'" if status else "has no status"


def reference_problem(path, text):
    """Why the plan's specs and ADRs do not let it be Ready to build, or None if they do."""
    specs, problem = named_specs(path, text)
    adrs, adr_problem = named_adrs(path, text)
    if problem or adr_problem:
        return problem or adr_problem
    if not specs and not adrs:
        return "it names nothing to build: list a spec and its requirements under Specs, or an ADR under ADRs"
    for spec_path, link, names in specs:
        if not is_spec(spec_path):
            return f"{link} is not a spec: a spec is a `.spec.md` file under docs/specs/"
        spec_text = read(spec_path)
        if spec_text is None:
            return f"the spec {link} does not exist"
        status = lifecycle_status(spec_text, SPEC_STATUSES)
        if status != ACCEPTED:
            return f"the spec {link} {described(status)}, not `{ACCEPTED}`"
        if not names:
            return (f"no requirement is named under {link}; list each one beneath it as "
                    "`  - [<requirement name>](<path>#<heading anchor>)`")
        anchors = spec_anchors(spec_text)
        numbered = set(anchors)
        for name, requirement_path, anchor in names:
            if name not in numbered:
                if old_layout(spec_text):
                    return old_layout_problem(link)
                if LEADING_NUMBER.sub("", name) in numbered:
                    return (f"the requirement link '{name}' gives the requirement's number; give the name "
                            f"alone as its text, as [{LEADING_NUMBER.sub('', name)}], since numbers "
                            "change when requirements are added or removed")
                return f"the spec {link} has no requirement named '{name}'"
            wanted = f"{link.split('#', 1)[0]}#{anchors[name]}"
            if requirement_path != spec_path or anchor != anchors[name]:
                return (f"the requirement link '{name}' must point to its heading in the spec it is "
                        f"listed under, as `[{name}]({wanted})`")
    for adr_path, link, number, title in adrs:
        if not is_adr(adr_path):
            return f"{link} is not an ADR: an ADR is a file in docs/adrs/"
        adr_text = read(adr_path)
        if adr_text is None:
            return f"the ADR {link} does not exist"
        status = lifecycle_status(adr_text, ADR_STATUSES)
        if status != ACCEPTED:
            return f"the ADR {link} {described(status)}, not `{ACCEPTED}`"
        own = re.match(r"\d{4}(?=-)", os.path.basename(adr_path))
        if own and number != own.group():
            return f"the link to {link} must show the ADR's number, as [{own.group()}]"
        actual = title_of(adr_text)
        if actual and title != actual:
            return f"the Decision beside {link} must be the ADR's title, word for word: '{actual}'"
    return None


def overlap_problem(path, text):
    """Why another unbuilt plan blocks this one, or None if none names the same requirement."""
    wanted = requirements(path, text)
    folder = os.path.dirname(os.path.abspath(path))
    for name in sorted(os.listdir(folder)):
        other = os.path.join(folder, name)
        if name == os.path.basename(path) or not name.lower().endswith(".md") or not os.path.isfile(other):
            continue
        other_text = read(other) or ""
        if lifecycle_status(other_text, STATUSES) not in (DRAFT, READY):
            continue
        shared = sorted(requirement for _, requirement in wanted & requirements(other, other_text))
        if shared:
            return f"the plan {name} already names the requirement '{shared[0]}'; change that plan instead"
    return None


def plan_rules(path, before, after, old, new):
    name = os.path.basename(path)
    if old not in STATUSES:
        return None
    if old == BUILT and not (new == old and (after == before or restyled(before, after))):
        return (
            f"{name}: this plan is `{BUILT}`, so it is frozen: it is never changed, though it may be "
            "deleted. For more work on the same requirements, write a new plan."
        )
    if new == old:
        if new != DRAFT and without_status(after) != without_status(before):
            return (
                f"{name}: this plan is `{old}`, so changing it must also set its status back to "
                f"`{DRAFT}`, for the person to sign off again."
            )
        return None
    if new == BUILT:
        return (
            f"{name}: only `/build`'s hand-over script sets `{BUILT}`, once every review of the "
            "build has passed. Leave the status as it is."
        )
    if old == READY and new != DRAFT:
        return f"{name}: a `{old}` plan can only go back to `{DRAFT}`, not to `{new}`."
    if new == READY:
        if without_status(after) != without_status(before or ""):
            return (
                f"{name}: set `{READY}` on its own, as the last edit after the person signs the "
                "plan off; this edit also changes the plan's content."
            )
        if has_open_questions(after):
            return (
                f"{name}: it still has open questions, so it cannot be `{READY}`. Settle them "
                f"with the person, or leave the plan as `{DRAFT}`."
            )
        problem = reference_problem(path, after) or overlap_problem(path, after)
        if problem:
            return f"{name}: it cannot be `{READY}`: {problem}."
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
    if lifecycle_status(text, ADR_STATUSES) != ACCEPTED:
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
        if new != DRAFT and after != before and not restyled(before, after):
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
        if new == ACCEPTED and has_open_questions(after):
            return open_questions_refusal(name, after, ACCEPTED, "ADR")
        if new == ACCEPTED and section(after, "Decision") is None and section(after, "Decision Outcome") is not None:
            return (
                f"{name}: this draft ADR is in the layout from before Question, Decision and Technical "
                f"detail, so it cannot be `{ACCEPTED}` as it stands. Re-lay it from the ADR template, "
                "have it reviewed, and ask the person again."
            )
        if new == ACCEPTED and not decision_chosen(after):
            return (
                f"{name}: its Decision section must open with \"Chosen:\" and name the option in full, "
                f"so the ADR cannot be `{ACCEPTED}` as it stands. Write the person's choice there, have "
                "it reviewed, and ask them again."
            )
        words = plain_words(after, ADR_DETAIL, ADR_DIAGRAMS) if new == ACCEPTED else 0
        if words > ADR_PLAIN_LIMIT:
            return (
                f"{name}: its plain part, from the title down to {ADR_DETAIL}, holds {words} words, more "
                f"than the {ADR_PLAIN_LIMIT} a person is asked to read, so it cannot be `{ACCEPTED}`. "
                f"Shorten it, moving detail down into {ADR_DETAIL}, and have it reviewed again."
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


def runs(text):
    """The Runs section without HTML comments or surrounding blank lines; "" when it holds none.

    Comments are found by scan(), so a run's output can never hide another run, and an unclosed
    `<!--` can never hide a run added below it.
    """
    return uncommented(section(text, "Runs") or []).strip()


def diagram_lines(lines, heading):
    """For each line, True if it is part of a closed fenced `mermaid` block inside the `## <heading>`
    section, fences included.

    A diagram there draws only what the text around it says (rubric check 18 of the ADR rubric),
    so it adds nothing for a person to read. A block left open runs to the end and is not a
    diagram, so an unclosed fence can never hide prose from the count, nor can a diagram anywhere
    else.
    """
    fenced, _ = scan(lines)
    allowed = headings_allowed(lines)
    diagram = [False] * len(lines)
    start = next((i for i, line in enumerate(lines) if allowed[i] and line.strip().lower() == "## " + heading.lower()), None)
    if start is None:
        return diagram
    stop = next((i for i in range(start + 1, len(lines))
                 if allowed[i] and (lines[i].startswith("# ") or lines[i].startswith("## "))), len(lines))
    i = start + 1
    while i < stop:
        match = FENCE.match(lines[i]) if fenced[i] else None
        if not match:
            i += 1
            continue
        fence, words = match.group(1), match.group(2).split()
        end = next((j for j in range(i + 1, stop) if fenced[j] and closes_fence(lines[j], fence)), None)
        if end is None:
            break
        if words and words[0].lower() == "mermaid":
            diagram[i:end + 1] = [True] * (end + 1 - i)
        i = end + 1
    return diagram


def plain_part(text, end_heading="Experiment", diagrams_in=None):
    """A document's plain part: its lines after the frontmatter and before the `## ` heading that
    starts its technical part (Experiment in a spike record, Technical detail in an ADR), joined,
    without HTML comments, and without the `mermaid` diagrams of the `## <diagrams_in>` section if
    one is named (Decision in an ADR). A document without that heading is plain to its end."""
    lines = text.lstrip("\ufeff").splitlines()
    head = frontmatter(text)
    lines = lines[len(head) + 2:] if head is not None else lines
    allowed = headings_allowed(lines)
    stop = "## " + end_heading.lower()
    end = next((i for i, line in enumerate(lines) if allowed[i] and line.strip().lower() == stop), len(lines))
    lines = lines[:end]
    if diagrams_in is None:
        return uncommented(lines)
    diagram = diagram_lines(lines, diagrams_in)
    return uncommented(["" if diagram[i] else line for i, line in enumerate(lines)])


def plain_words(text, end_heading="Experiment", diagrams_in=None):
    """How many words a document's plain part holds, leaving out the diagrams of `diagrams_in`."""
    return len(WORD.findall(plain_part(text, end_heading, diagrams_in)))


def decision_chosen(text):
    """Whether an ADR's Decision, without comments, opens with "Chosen:" (bold or not) and goes on
    to name the option."""
    decision = uncommented(section(text, "Decision") or []).strip()
    return re.match(r"[*_]*chosen[*_]*:[\s*_]*[^\s*_]", decision, re.IGNORECASE) is not None


def finding_opens_with(text, word):
    """Whether a spike record's Finding, without comments, opens with `word` (any case, bold or
    not), followed by more than the word itself."""
    finding = uncommented(section(text, "Finding") or []).strip().lstrip("*_ ")
    match = re.match(re.escape(word) + r"\b[*_]*[:.,;]?[*_]*\s*(\S)", finding, re.IGNORECASE)
    return match is not None


def uncommented(lines):
    """The lines joined with newlines, without the HTML comments scan() finds in them."""
    _, comments = scan(lines)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line) + 1)
    joined, kept, at = "\n".join(lines), [], 0
    for (line, column), (end_line, end_column) in comments:
        kept.append(joined[at:starts[line] + column])
        at = starts[end_line] + end_column
    kept.append(joined[at:])
    return "".join(kept)


def ran(text):
    """Whether Runs holds a run that happened: one whose heading line doesn't say "did not run"."""
    lines = runs(text).splitlines()
    allowed = headings_allowed(lines)
    for i, line in enumerate(lines):
        if allowed[i] and re.fullmatch(r"### Run \d+\s*", line):
            stamp = next((later for later in lines[i + 1:] if later.strip()), "")
            if not stamp.rstrip().endswith("did not run"):
                return True
    return False


def spike_rules(path, before, after, old, new):
    name = os.path.basename(path)
    if old not in SPIKE_STATUSES:
        if runs(after):
            return f"{name}: a new spike record starts with Runs empty; only the run script adds runs."
        return None
    if old in FINISHED:
        # Only a `type:` line may be added, which without_status() leaves out, and the status
        # written with its emoji if it lacked one, as an old record's may.
        if new == old and restyled(before, after):
            return None
        return (
            f"{name}: this spike record is `{old}`, which is final, so it is never changed. "
            "Another try at the hypothesis is a new spike record."
        )
    if runs(after) != runs(before):
        return (
            f"{name}: only the run script writes the Runs section, so the results are exactly what "
            "the experiment produced. Leave Runs as it is and run the experiment through the script."
        )
    moves = {DRAFT: (READY_TO_RUN,), READY_TO_RUN: (DRAFT,) + FINISHED}
    if new != old and new not in moves[old]:
        return (
            f"{name}: a spike record cannot go from `{old}` to `{new}`. `{DRAFT}` becomes "
            f"`{READY_TO_RUN}`; `{READY_TO_RUN}` becomes {listed(FINISHED)}, or "
            f"`{DRAFT}` before the first run."
        )
    if new == DRAFT and old == READY_TO_RUN and runs(before):
        return (
            f"{name}: the experiment has already run, so the record cannot go back to `{DRAFT}` "
            "after the first run. A different hypothesis or experiment is a new spike record."
        )
    if new in (READY_TO_RUN,) + FINISHED and new != old:
        if without_status(after) != without_status(before):
            return (
                f"{name}: set `{new}` on its own, as the last edit after a passing review and the "
                "person's sign-off; this edit also changes the record's content."
            )
        if has_open_questions(after):
            return open_questions_refusal(name, after, new, "spike record")
        words = plain_words(after)
        if words > PLAIN_LIMIT:
            shorten = ("Shorten its Finding, Next steps, Results or Surprises, since the rest is fixed"
                       if new in FINISHED else "Shorten it, moving detail down into Experiment")
            return (
                f"{name}: its plain part, from the title down to Experiment, holds {words} words, "
                f"more than the {PLAIN_LIMIT} a person is asked to read, so it cannot be `{new}`. "
                f"{shorten}, and have it reviewed again."
            )
        if new in (CONFIRMED, REFUTED) and not ran(after):
            return (
                f"{name}: it has no runs, so it cannot be `{new}`: only an experiment's runs "
                f"settle a spike. Run it through the run script, or end it `{NOT_SETTLED}`."
            )
        word = new.split(" ", 1)[1]
        if new in FINISHED and not finding_opens_with(after, word):
            return (
                f"{name}: its Finding must open with \"{word}\", the status it is given, then say what "
                f"was found, so the record cannot be `{new}` as it stands. Correct the Finding, or "
                "give the status its first word names."
            )
    if old == new == READY_TO_RUN:
        changed = [part for part in FIXED_PARTS if section(after, part) != section(before, part)]
        if changed:
            return (
                f"{name}: the record is `{READY_TO_RUN}`, so its {', '.join(changed)} section is "
                f"fixed. To change it before the first run, also set the status back to `{DRAFT}` "
                "for the person to sign off again."
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
