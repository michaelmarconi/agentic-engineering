---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: 👍 Accepted
date: 2026-10-28
---

# Check corrections instead of reviewing again

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. The
plugin helps a person write the documents of a software project, such as a spec, which says what
one feature must do. Each kind of document has a skill: a set of instructions Claude follows to
write it with the person. While Claude writes, we call it the drafting agent.

Before the person sees a document, a reviewer checks it. The reviewer is an agent: a separate
instance of Claude, started with its own instructions and none of the conversation, so it reads
the document as a newcomer would. It checks the document against the skill's rubric, a short
list of pass-or-fail checks such as "each requirement states exactly one rule". Its report lists
findings. A failure breaks a check and must be corrected. A decision is something only the person
can settle, such as which of two meanings they intended. A suggestion is optional.

Until now the drafting agent corrected the failures and ran the reviewer again, repeating until
a review passed or a maximum number of reviews was reached. Each person had to choose that maximum
in the plugin's settings before their first review. The loop seldom finished cleanly, so we
measured it.

We had a separate Claude write 10 short specs for a made-up product and plant 21 mistakes in 8
of them, leaving 2 with none. We ran each way of reviewing 3 times on each spec, so each option
had 30 runs and 63 chances to catch a planted mistake (21 mistakes, 3 runs each). In the figures
below:

- A mistake is **caught** when some review in the run pointed it out, and **left** when it is
  still in the document the run ended with. A caught mistake can still be left, for example when
  its correction went wrong.
- A **new problem** is a mistake that a correction introduced.
- Mistakes left and new problems were counted by Opus, Anthropic's largest model, reading the
  document each run ended with. The reviewers ran on Sonnet, its mid-sized model.
- A run **passes** when its last review or check reports no failures. This is the plugin's own
  verdict, not a count of mistakes left.
- **Cost** is the price Anthropic charges for the models' use in a run.

We need a review that catches as many mistakes as before, introduces as few new ones as possible,
always ends with a clear result, and needs no setting.

## Considered Options

- **Review again after each correction, up to a set number of reviews**, as before. Rejected:
  only 17 of 30 runs passed, so most runs ended at the maximum without a clear result. The first
  review caught 94% of the 63 planted mistakes, and all its reviews together 95%, so later reviews
  added almost nothing, while the corrections introduced 1.6 new problems per run. It also
  needs the setting.
- **Several reviewers, each looking for one kind of problem, plus one more that checks their
  findings.** Rejected: they caught 100% of the planted mistakes, against 95% for the option above,
  but at 4 times the cost, and only 9 of their 30 runs passed. On the 2 specs with no planted
  mistakes, where findings are mostly false alarms, their first review reported 3.5 findings
  against 1.8.
- **The usual reviewer on Opus instead of Sonnet.** Rejected: it caught about as many (97% against 95%) at twice the cost. Its runs left
  6 of 63 planted mistakes, introduced 1.9 new problems per run, and 13 of 30 passed.
- **One reviewer with two modes, a full review or a check of the corrections only.** Rejected:
  a reviewer told to check only the corrections can drift into reviewing the whole document
  again, which brings back the repeated reviews.
- **Marking findings and corrections inside the document**, as tracked changes in CriticMarkup
  (a plain-text notation for edits and comments), so that a reviewer re-reads only the marked
  parts. Rejected: too much extra machinery. It needs editing tools that enforce the notation
  and a step that removes it before the person approves the document. The reviewer is also
  only allowed to read files, so it cannot add marks.
- **Review once, correct once, then check only the corrections.** Chosen, below.

## Decision Outcome

Chosen option: review once, correct once, then check only the corrections, because on the same
specs it ended with the best documents at the lowest cost. It catches slightly fewer mistakes
than several reviewers: its one review is the same as the first review above, which caught 94%.
But at the end of a run it did as well as or better than every other option:

- Planted mistakes left: 3 of 63, the same as the several reviewers (repeated reviews left 5,
  the Opus reviewer 6).
- New problems from corrections: 1.1 per run, the fewest.
- Runs that passed: 26 of 30, the most.
- Cost: 0.6 times that of repeated reviews, the least.

The sequence is fixed:

1. **Review.** The skill's reviewer checks the whole document against the rubric.
2. **Correct.** The drafting agent reads the rubric again and corrects only the failures in the
   report, once. Each decision becomes an entry in the document's list of open questions for the
   person. Suggestions are left alone, and nothing else changes. These instructions must be this
   narrow. In the first measurement, where the drafting agent had them, 26 of 30 corrected
   documents passed the check that follows. In a second measurement on the same specs, where it
   lacked them, only 41 of 90 did.
3. **Correction check.** A second agent, the correction checker, the same one for every skill,
   compares the document before and after the corrections. It checks only that each failure was
   corrected and that no correction broke anything. Anything else it notices is a suggestion.
4. If the review found no failures, or the check passes, the drafting agent shows the person the
   document and both reports. If the check fails, the drafting agent stops and shows the person
   what failed, rather than correcting again.

If the person later asks for changes, the same sequence runs again on the changed document. That is
not the loop rejected above, which reviewed again to find out whether its own corrections were
right. Here a new review happens only because the person changed the document, and each review
is still followed by at most one round of corrections and one check.

### Consequences

- Good: every review ends with a clear result, and costs less than before.
- Good: there is no setting to make before the first review.
- Bad: a mistake the one review misses stays in the document. In the measurement, 3 of 63
  planted mistakes were still there at the end.
- Bad: when the check fails, the person has to step in, where further rounds might sometimes have
  fixed it without them.
- Bad: the check is not perfect. In the measurement, about one new problem from corrections per
  run got past it.

### Confirmation

Applies to: any skill whose documents are reviewed before the person sees them.
Checked by: automated tests that run each skill on sample conversations and grade what it did.
They check that each document is reviewed at most once per request from the person, corrected
at most once, and that every correction is followed by a correction check. One test swaps in a
fake correction checker that always fails, and checks that the skill stops and shows the person
without reviewing or correcting again.
