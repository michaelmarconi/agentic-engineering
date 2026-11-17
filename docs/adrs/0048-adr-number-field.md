---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0048
status: 👍 Accepted
date: 2026-11-17
---

# Show each ADR's number in a number field, checked against its file name

## Question

How does a reader of an ADR[^adr] see its number?

## Decision

Chosen: every new ADR holds a `number:` field in its frontmatter[^frontmatter], right after
`type:`, giving the four-digit number from its file name; a hook[^hook] refuses a number that does
not match the file name, and the audit[^audit] lists older ADRs without one. The number is shown
where the other fields already are, and the file name stays the one place the number comes from.

## Background

An ADR's number lives only in its file name, such as `0047-...md`. Other ADRs refer to it by that
number, in the `supersedes:` and `superseded-by:` fields, yet the page a reader sees shows only the
type, status and date. [ADR 0027](0027-status-change-record.md) added `date:` to the frontmatter,
and let documents written before it go without one and gain one with any edit.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Leave the number in the file name only | Rejected | A reader of the page still cannot see the number other ADRs use |
| Put the number in the title | Rejected | It mixes a label into the title, which says what was decided |
| A `number:` field, checked against the file name | Chosen | It sits beside the other fields, and the check stops it from disagreeing with the file name |
| The same rule for every kind of document whose name starts with a number or date | Rejected | Only ADRs are numbered; plans[^plan] and spike records[^spike] would gain a second date beside `date:`, which would confuse readers |
| A script that fills in the field on every existing ADR | Rejected | A one-off change to accepted, rejected or superseded ADRs that nobody asked for; the audit lists them for the person instead |

## Consequences

- Good: a reader sees the ADR's number on the page, beside its type, status and date.
- Good: the hook refuses a field that differs from the file name.
- Bad: renumbering an ADR, as when two branches pick the same number, means changing the field as well as the file name.

## Out of scope

- Anything reading the field: the plugin[^plugin] keeps taking the number from the file name.
- Specs[^spec], plans, spike records and the brief[^brief], which gain no such field.
- ADRs written before the field. Each may go without one, and may gain a matching one with any edit, even an ADR whose decision is already made or replaced.

## How we'll check

Applies to: every change that writes an ADR.

1. Test: unit tests give the hook new ADRs and edits, and check what it allows and refuses.
2. Test: a sample conversation with the ADR skill[^skill] ends with a new ADR holding the right number.
3. Test: unit tests check that the audit lists an ADR with no `number:` field.

## Open questions

- None.

## Technical detail

**The field.** `number:` holds the four digits that start the file's name, such as `number: 0048`,
on the line after `type:`. The ADR template carries it, and the ADR skill fills it in when it picks
the file's number.

**The hook.** `scripts/status_check.py` refuses, for a file in `docs/adrs/`:

- a new ADR with no `number:` line, or more than one;
- a `number:` that is not the four digits starting the file's name;
- taking `number:` away once the ADR has one.

A change to `number:` is allowed only when the new value matches the file's name, as after a
renamed file.

Adding a matching `number:` to an ADR that has none is allowed with any edit, whatever its status,
in the way a missing `type:` or `date:` may be added: the rules that forbid edits to an accepted,
rejected or superseded ADR leave the line out when comparing the text before and after the edit.

**Audit.** `/audit` lists each ADR with no `number:` field, beside the documents it already lists
with no `date:`, as the person's checklist for filling them in by hand.

[^adr]: An ADR (architecture decision record) is the write-up of one technical decision and why it was made.
[^frontmatter]: The frontmatter is the block of settings at the top of a document, such as its type and status.
[^hook]: A hook is a script Claude Code runs automatically at set moments, here just before Claude edits a file.
[^audit]: The audit is the plugin's step that checks every document, and the code against them.
[^plan]: A plan sets out one piece of work that builds part of a spec or an ADR.
[^spike]: A spike record is the write-up of one throwaway experiment that settles an unknown.
[^plugin]: The plugin is the agentic plugin for Claude Code, which holds the lifecycle's skills and hooks.
[^spec]: A spec says what one capability of the product should do.
[^brief]: The brief is the one document that says what the product is, who it is for and why.
[^skill]: A skill is a set of instructions Claude follows for one step, run as a slash command.
