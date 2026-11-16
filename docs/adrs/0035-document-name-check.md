---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: 2026-11-16
---

# Check each document's name by one rule when it is written

## Question

When, and by what, is the file name of each lifecycle document[^document] checked?

## Decision

Chosen: one naming rule, with a form for each kind of lifecycle document but the brief, checked by
the hook[^hook] that checks each write. A name is a number, or the date the document is written,
then a subject of two to five words, each a word of the document's title. The hook refuses a new
document whose name breaks the rule, and an edit that drops a subject word from the title. The
audit[^audit] checks an existing document's name for its shape only, so no accepted record is
renamed. A name checked this way is right before any review[^review], so no review asks for a
rename.

## Background

[ADR 0011](0011-review-relay-hook.md) has a hook keep a copy of each document under review, and
finds that copy by the document's file path, so a renamed document's corrections cannot be checked. Today only reviewers check names, each by its own rule, so a review can ask for a rename that breaks the correction check[^check].

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Keep checking names in each reviewer | Rejected | A review can still ask for a rename |
| Have the review hook follow a renamed document | Rejected | The hook would guess which file became which |
| Reviewers check names, and renames wait until after review | Rejected | A wrong name is found only once the review has started |
| One rule, checked by the write hook, with the subject's words in the title | Chosen | Names are right before review, by an exact check |

## Consequences

- Good: a review never fails a name given under the rule.
- Good: every name matches words in its title, and a plan's name no longer repeats its whole title.
- Bad: a correction rewording the title must keep the subject's words.
- Bad: a name from before the rule may hold words its title lacks.

## Out of scope

- Keeping a document's name while its review runs, which [ADR 0036](0036-keep-name-review.md) decides.
- Writes made by a shell command, which no hook sees.

## How we'll check

Applies to: any skill[^skill], rubric[^rubric] or hook that names or checks the name of a lifecycle document.

1. Test: the write hook refuses a badly named new document of each kind.
2. Test: the write hook refuses an edit dropping a subject word from the title.
3. Test: a document named before the rule stays editable.
4. Test: the audit lists names of the wrong shape only.
5. Inspection: no rubric checks a name's form.
6. Demonstration: an install refuses a new ADR named with one word.

## Open questions

None.

## Technical detail

**The rule.** The subject is two to five words of lowercase letters and digits, joined by single
hyphens: `[a-z0-9]+(-[a-z0-9]+){1,4}`. Each of its words is a word of the document's `# ` title,
compared in lowercase with the title split at every character that is not a letter or a digit, so
"document's" holds "document" but "documents" does not. Each kind's name is:

| Kind | Name |
| --- | --- |
| Brief | `docs/brief.md`, fixed |
| Spec | `docs/specs/**/<subject>.spec.md`; the folders below `docs/specs/` are not checked |
| ADR | `docs/adrs/NNNN-<subject>.md`, four digits no other file in the folder starts with |
| Plan | `docs/plans/YYYY-MM-DD-<subject>.md`, the date it was written, so today's date |
| Spike record | `docs/spikes/YYYY-MM-DD-<subject>.md`, the date it was written, so today's date |

A plan's subject is no longer its whole title, only words from it, so it stays two to five words.
Today's date is the one the `date:` field must already carry on a new document.

**The write hook.** `status_check.py`, on Write, Edit and MultiEdit, refuses the creation of a
spec, ADR, plan or spike record (no file at that path on disk, and a lifecycle status or `type:`
in what is written) whose name breaks the rule. Its reason gives the form the name should take.
For an existing file it refuses only an edit after which the title lacks a word of the name that
the title held before, so a file named before the rule can still be edited; the hook never sees a
rename, so it never refuses a file for its name alone.

**The audit.** `/audit`'s document check lists every spec, ADR, plan and spike record whose name
has the wrong shape: the number or date, then the subject's two to five words. It does not compare
the subject with the title, nor the date with today's. A document's number or date is its lasting
identity, while other documents link to its full file name, and an accepted ADR cannot be edited
to follow a rename, so names from before the rule are left as they are.

**Reviewers.** No rubric checks the name's form or its words any more, since the hook does both:
the shape checks of the ADR, plan and spike rubrics drop their file name rules, including the ADR
rubric's three to five words.

[^document]: A lifecycle document is one of the plugin's five kinds of document: the brief, which says what the product is; a spec, what one capability should do; an ADR (architecture decision record), one technical decision; a plan, one piece of work; and a spike record, one experiment.
[^hook]: A hook is a script Claude Code runs automatically at set moments, such as before Claude writes a file or starts an agent.
[^review]: A review is the plugin's fixed sequence for each document: separate agents review it, Claude corrects it once, and another agent checks the corrections.
[^check]: A correction check is a separate agent's check that the corrections made after a review were made, and broke nothing.
[^audit]: The audit is the plugin's step that checks whether the code and the project's documents still agree.
[^skill]: A skill is one of the plugin's sets of instructions Claude follows for one step.
[^rubric]: A rubric is the list of checks a reviewer applies to one kind of document.
