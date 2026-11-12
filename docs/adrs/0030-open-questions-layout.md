---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: 2026-11-11
---

# Show every proposal in a block quote, in documents and in the conversation

## Question

How does the plugin lay out each question it puts to the person[^person], in a document's[^documents]
open questions[^open] or in the conversation, so they can find the proposal quickly?

## Decision

Chosen: each open question is a numbered heading, then its context, then a block quote[^quote]
holding one line starting "**Proposed:**", with the answer alone, and one starting "**Why:**", with
the reason. A question asked in the conversation has the same parts after a bold line naming it, and
ends with the question. The hook[^hook] refuses an edit that adds or changes Open questions in
another layout, and the audit[^audit] lists documents not in it. The block quote is easy to see on
GitHub, in an editor and in the conversation, and a script can check it.

## Background

The plugin's skills[^skill] end each open question with "Proposed:" and an answer, inside the
question's paragraph. There it is easy to miss, and a second proposal can go unnoticed next to it.
[ADR 0005](0005-status-change-hook.md) set up the hook that checks the documents as Claude writes
them.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Keep "Proposed:" at the end of the paragraph | Rejected | The part the person acts on is the hardest to find |
| A bold "Proposed:" label in its own paragraph | Rejected | The reason ends up mixed into the proposal again |
| The proposal before the context | Rejected | It reads oddly when the proposal needs the context |
| A heading, the context, then a block quote holding "Proposed:" and "Why:" | Chosen | Easy to see wherever Markdown is read, even raw |
| A GitHub callout box | Rejected | Only GitHub draws the box; elsewhere a line of raw markup appears |
| A one-cell table | Rejected | Hard to edit, and long text wraps badly |
| An arrow emoji before "Proposed:" | Rejected | Emoji are kept out of the documents' prose |

## Consequences

- Good: each proposal, and its reason, can be found quickly.
- Good: one layout holds for all five kinds of document and for the conversation.
- Bad: an open question takes more lines than before.

## Out of scope

- Edits made by hand, which the hook never sees.
- Whether a proposal makes one decision, which the separate Claude reviewer that checks each document judges.
- Documents written before this, which keep their old layout until their Open questions next change.

## How we'll check

Applies to: every open question in a brief, spec, ADR, plan or spike record, and every question a
skill asks the person in the conversation.

1. Test: unit tests give the hook Open questions in and out of the layout, and check what it allows and refuses.
2. Test: unit tests check that the audit lists documents whose Open questions are not in the layout.
3. Test: for each skill that writes one of the five documents, a sample conversation writes its open questions in the layout.
4. Test: for each skill that asks the person questions, a sample conversation asks one in the layout.

## Open questions

- None.

## Technical detail

**The layout.** Under `## Open questions`, either "None." (or "- None.") or a run of entries. Each
entry is a heading `### N. <what is to be settled>`, numbered from 1 in order; at least one line of
context; then one block quote, last in the entry, holding exactly one line starting
`> **Proposed:**` and, after it, exactly one line starting `> **Why:**`. Where only the person can
know the answer, "Proposed:" says what would settle it. HTML comments are ignored.

```markdown
### 1. Where the daily tariff copy is kept

The tariff is copied daily, but where is not yet chosen.

> **Proposed:** Object storage, one file per day.
>
> **Why:** The copy is read whole once a day and never queried.
```

**The hook.** `scripts/status_check.py` refuses a Write, Edit or MultiEdit to the brief, a spec,
an ADR, a plan or a spike record when its Open questions section is new or differs from the file on
disk, and any entry in it breaks the layout. The refusal names the entry and what is wrong.

**In the conversation.** A question asked in the conversation starts with a bold line such as
"**Question 1 of 3: how often a failed pull is retried**", then the context, then the same block
quote, then the question itself in one line. One sentence, copied word for word into every skill
that asks the person to settle questions, says so. No hook can see the conversation, so tests check
it.

**Audit.** The audit's document check lists each document whose Open questions are not in the
layout, so older documents have a list to work through.

[^open]: An open question is something only the person can settle, listed in the document's Open questions section until they do.
[^documents]: The plugin writes five kinds of document: the brief, which says what the product is and who it is for; specs, which say what one capability should do; ADRs (architecture decision records), each the write-up of one technical decision; plans, each setting out one piece of work; and spike records, each the write-up of one throwaway experiment.
[^person]: The person is whoever is working with Claude and the plugin on the project.
[^quote]: A block quote is a set of lines each starting with `>`, which Markdown shows set apart from the text around it.
[^hook]: A hook is a script Claude Code runs automatically at set moments, here just before Claude edits a file.
[^audit]: The audit is the plugin's step that checks every document, and the code against them.
[^skill]: A skill is a set of instructions Claude follows for one step, run as a slash command.
