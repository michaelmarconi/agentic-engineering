---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-10
supersedes: 0012
---

# Record the day of each status change in the document, and who approved it in the pull request

## Question

Where does the plugin record when a document's status last changed, and who approved that change?

## Decision

Chosen: every document with a status holds a `date:` field giving the day its status last changed.
A hook[^hook] refuses any status change Claude makes without today's date, and any other change to
the date; the audit[^audit] lists documents without one. The pull request[^pr] still records who approved
each change.

## Background

The plugin's skills[^skill] write specs[^spec], ADRs[^adr], plans[^plan] and spike records[^spike],
each with a status, such as Draft or Accepted. [ADR 0012](0012-approval-record.md) left who and when
to the pull request, yet ADRs carry a date with no stated meaning, and the others carry none.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| No fields: the pull request records who and when, as [ADR 0012](0012-approval-record.md) chose | Rejected | A reader must search the history to find when |
| A date for the day the document was first written | Rejected | Plans and spike records already carry that day in their file names |
| A date for the day the document was last edited | Rejected | That date repeats git, the version control system, and falls out of date |
| A date for the day the status last changed, checked by the hook, with who approved left to the pull request | Chosen | This date gives how long the current status has held, under one rule for all four kinds |
| Fields for the day and for the name of who approved | Rejected | Anyone can type any name; the pull request uses signed-in accounts |

## Consequences

- Good: a reader sees at once how long a spec has been accepted, a plan built or a spike settled.
- Good: one rule holds for all four kinds of document.
- Bad: replacing an ADR with a newer one changes its date, so the day it was accepted is then found only in git.

## Out of scope

- The brief[^brief], which has no status, so it has no date.
- Edits made by hand, which the hook never sees.
- A project that merges changes without pull requests, which has no record of who approved them.
- Documents written before the field. Each may go without a date until its next status change. Adding one, any real date, is allowed with any edit, even to an accepted ADR, a built plan or a finished spike record.

## How we'll check

Applies to: every change that writes a spec, ADR, plan or spike record, or changes its status.

1. Test: unit tests give the hook new documents, status changes and other edits, and check what it allows and refuses.
2. Test: unit tests check that the build step dates a plan when it marks the plan Built.
3. Test: for each skill that changes a status, a sample conversation ends with the document's date set.
4. Test: unit tests check that the step that checks documents against the code reports a missing or malformed date.

## Open questions

- None.

## Technical detail

**The field.** `date:` sits in the frontmatter of every spec, ADR, plan and spike record, as
YYYY-MM-DD. Each template carries it under `status:`.

**The hook.** `scripts/status_check.py`, the status hook of [ADR 0005](0005-status-change-hook.md),
runs before each Write, Edit or MultiEdit. For a document with a status before or after the edit, it
refuses:

- more than one `date:` line, or a date that is not a real YYYY-MM-DD date;
- a new document, or any status change, whose `date:` is not today's date on the machine running it;
- a change to `date:`, or taking it away, while the status stays the same; adding one to a document
  that has none is not a change, and may be any real date.

The hook's rules that a status be set with no other change in the same edit, for
accepting a spec or an ADR, rejecting an ADR, signing off a plan and moving a spike record forward,
let the `date:` line change with it.

**Built plans.** The script that `/build` runs at the end marks a plan Built by writing the file
directly, not through Claude's file-editing tools, so the hook never sees that change; the script
sets `date:` to the same day.

**Audit.** `/audit`, the skill that finds where the code and its documents disagree, reports each spec, ADR, plan or spike record with no `date:` or a malformed one.

**Tests.** Today's date is passed into the hook's tests, never read from the clock.

[^hook]: A hook is a script Claude Code runs automatically at set moments, here just before Claude edits a file.
[^pr]: A pull request is a proposed change that a person reviews and approves on a code-hosting service, such as GitHub, before it is merged.
[^skill]: A skill is a set of instructions Claude follows for one step, run as a slash command.
[^spec]: A spec says what one capability of the product should do.
[^adr]: An ADR (architecture decision record) is the write-up of one technical decision and why it was made.
[^plan]: A plan sets out one piece of work that builds part of a spec or an ADR.
[^spike]: A spike record is the write-up of one throwaway experiment that settles an unknown.
[^audit]: The audit is the plugin's step that checks every document, and the code against them.
[^brief]: The brief is the one document that says what the product is and who it is for.
