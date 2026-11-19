---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0053
status: Draft 📝
date: 2026-11-19
---

# Write the review sequence once, on the lifecycle page, for every skill to read

## Question

Where is the review sequence[^sequence] written, so that every skill[^skill] that runs it follows
the same words?

## Decision

Chosen: write the sequence once, in the Review section of the plugin's lifecycle page[^lifecycle],
for both a person and Claude to follow. Each skill that runs it reads that section at its review
step, through one sentence worded the same in every skill, and keeps only what is its own:

- its reviewer agent and the request it sends;
- its rubric[^rubric];
- the status[^status] it moves its document to, if any;
- the sentence on showing the person the finished document, which
  [ADR 0025](0025-document-review-display.md)[^adr] has every skill keep.

A single copy cannot come to differ from another.

## Background

[ADR 0049](0049-review-once-check-changes.md) settled what the sequence does: review once, correct
once, then check only what changes, with the person deciding each question. Eight skills carry
their own copy, each 1,300 to 1,900 tokens long. A script checks that some of its sentences are
identical in every skill; the rest now differ, with eight wordings of how a decision becomes a
question. Two skills are within 3 tokens of the 5,000-token limit per skill. The skills already open the lifecycle
page by its path for its rule that documents use words a newcomer can follow.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Keep a copy in each skill, as now | Rejected | Copies come to differ, and they fill the skills' size limit |
| Have the script check every shared sentence | Rejected | Stops the differences, but worsens the size problem |
| A separate file that only Claude reads | Rejected | Splits the rules across two places |
| The lifecycle page's Review section, read by each skill | Chosen | One copy, which people and Claude both read |

## Consequences

- Good: the sequence has one wording, which the check script checks in one place.
- Good: each skill shrinks by about 1,500 tokens, after keeping its own parts.
- Bad: a skill must open another file at its review step, and might skim it rather than follow it.
- Bad: the Review section gets longer, and is written as steps to follow as well as a description.

## Out of scope

- What the sequence does: [ADR 0049](0049-review-once-check-changes.md).
- What the person is shown at the end: [ADR 0025](0025-document-review-display.md).
- The build skill's own sequence for code, which stays in that skill.
- How the rest of the lifecycle page is laid out.

## How we'll check

Applies to: every skill that has a document reviewed before the person signs it off.

1. Inspection: the sequence's shared steps appear in no skill, only on the lifecycle page.
2. Test: the check script fails a reviewing skill that lacks the sentence sending it to the Review section.
3. Test: the check script fails a lifecycle page whose Review section lacks a shared sentence.
4. Demonstration: each reviewing skill's existing evals for its review pass.

## Open questions

None.

## Technical detail

**Which skills.** /brief, /spec, /adr, /plan and /spike, which take the person's answers with four
choices (accept the proposal, give their own answer, ignore it or defer it), and /practices,
/feedback and /release, which stop and show the correction check's report when it fails. The Review
section describes both ways a review can finish, each under its own heading, and each skill's
sentence names the one it follows.

**What moves.** The Review section takes the steps now repeated in each skill: starting the
reviewer and `agents/language-checker.md` side by side, each request opening with the line
`Document: <path>`; correcting once; starting `agents/correction-checker.md`; and putting each
question to the person with the four choices. The sentences `scripts/skill_check.py` now checks
in each skill for those steps (`ANSWER_RULES`, `CORRECT_RULES` and `REVIEW_RULE`) move there
unchanged. One of them tells Claude to end a question with "Accept, give your own answer, ignore or
defer?", the line `scripts/review_relay.py` looks for in Claude's replies to save the person's
answer, so the line must not change. `SHOW_RULE` stays in each skill, as [ADR 0025](0025-document-review-display.md) requires. Each
skill keeps any step only it has, such as the diagram offer in /adr and /plan.

**What the check script checks.** `skill_check.py` checks that each reviewing skill holds the one
sentence, worded exactly, naming how its review finishes, and that the Review section holds each
moved sentence exactly. A unit test checks that the phrases `review_relay.py` looks for appear in
the Review section.

**The path.** Each skill opens the page by its path inside the plugin, as it does today for the
wording rule, so the sequence is there even in a repository without a brief or spec, where the page
is not given to Claude at the start of the session.

**The evals.** The evals are the plugin's recorded test cases, each a prompt run through Claude and
graded. Those for the review are the cases named after each skill that check its correction, its
check and its questions, such as `spec-corrects-once`, and the cases under `evals-failed-check/`.

[^sequence]: The review sequence is the fixed set of steps a document goes through before the person signs it off: a review by a separate Claude, one round of corrections, and a check of those corrections.
[^skill]: A skill is a set of instructions Claude follows for one step of the plugin, run as a command such as /spec.
[^lifecycle]: The lifecycle page is the plugin's one page of shared rules: the documents it keeps, the steps that write them and how they are reviewed. Claude is given it at the start of a session in a repository that has a brief, the document saying what the product is and who it is for, or a spec, a document saying what one capability of the product should do.
[^rubric]: A rubric is a skill's short list of pass-or-fail checks for its documents.
[^status]: A status is the field at the top of a document that says how far along it is, such as Draft or Accepted.
[^adr]: An ADR (architecture decision record) is a document recording one technical decision and why it was made.
