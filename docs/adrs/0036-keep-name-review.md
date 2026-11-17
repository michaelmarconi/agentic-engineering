---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: Accepted 👍
date: 2026-11-16
---

# Keep a document's name through its review, by one shared rule in every skill

## Question

What stops a lifecycle document[^document] being renamed while its review[^review] runs?

## Decision

Chosen: every skill[^skill] that writes a lifecycle document holds the same sentence, word for
word, forbidding a rename once the document's review has started, checked by the plugin's script
that checks skills. A name that never changes during a review lets the correction check[^check]
find the saved copy of the document it needs.

## Background

[ADR 0011](0011-review-relay-hook.md) has a hook[^hook] keep a copy of each document under review, and
find that copy by the document's file path, so the corrections of a renamed document cannot be
checked. [ADR 0035](0035-document-name-check.md) removes the usual reason for a rename, a
review that finds a bad name, but Claude can still rename a document for another reason. Today
only the spike skill forbids a rename.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Leave it to each skill | Rejected | Only the spike skill forbids a rename today, and the other skills say nothing |
| Have the review hook follow a renamed document | Rejected | The hook would have to guess which file became which |
| Have a hook refuse rename commands | Rejected | A shell command that renames a file cannot be recognised reliably |
| One shared sentence in every document skill | Chosen | The same rule everywhere, checked word for word |

## Consequences

- Good: the correction check finds the review it follows.
- Good: one sentence to change if the rule ever changes.
- Bad: a name that stops fitting during a review stays until the review has ended.

## Out of scope

- A rename the person asks for, during a review or after it, which starts a new review.
- How documents are named, which [ADR 0035](0035-document-name-check.md) decides.

## How we'll check

Applies to: every skill that writes a lifecycle document.

1. Test: the plugin's script that checks skills fails a document skill that lacks the shared sentence.
2. Inspection: the spike skill holds the shared sentence in place of its own.

## Open questions

None.

## Technical detail

**The sentence.** `scripts/skill_check.py` gains `RENAME_RULE`, held word for word by every skill in
`DOCUMENT_SKILLS` (brief, spec, adr, plan and spike):

> Never rename a document once its review has started: the review hook keeps the review under
> the document's path, so a renamed document's corrections can't be checked. If the name no
> longer fits, say so to the person, who can rename it once the review has ended.

It replaces the spike skill's own sentence, which says the same for spike records alone.

[^document]: A lifecycle document is one of the plugin's five kinds of document: the brief, which says what the product is; a spec, what one capability should do; an ADR (architecture decision record), one technical decision; a plan, one piece of work; and a spike record, one experiment.
[^review]: A review is the plugin's fixed sequence for each document: separate agents review it, Claude corrects it once, and another agent checks the corrections.
[^skill]: A skill is one of the plugin's sets of instructions Claude follows for one step.
[^check]: A correction check is a separate agent's check that the corrections made after a review were made, and broke nothing.
[^hook]: A hook is a script Claude Code runs automatically at set moments, such as before Claude writes a file or starts an agent.
