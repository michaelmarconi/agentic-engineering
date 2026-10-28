---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
date: 2026-10-28
---

# Review once, correct once, then check only the corrections

## Context and Problem Statement

Every document a skill writes is checked by a reviewer agent: a separate Claude that starts
without the conversation and checks the document against the skill's rubric. Until now the
drafting agent corrected what the reviewer found and ran the reviewer again, up to a number of
reviews each person had to set before their first review.

That loop rarely ended in a pass. We measured it on 10 specs for a made-up product, 8 of them
with 21 planted mistakes, 3 runs each. Later reviews almost never found a planted mistake the
first had missed; they found new, smaller problems, many of them made by the previous round's
corrections, and restated decisions only the person could make. We need a review that catches
as much, adds as few new problems as possible, ends with a definite result, and needs no setting.

## Considered Options

- **Repeated rounds up to a set limit**, as before. Lost: 17 of 30 runs ended in a pass; the
  first review already caught 94% of planted mistakes, and further rounds added about 1.6 new
  problems per run while finding almost nothing new. It also needs each person to save a setting.
- **Several reviewers, each looking for one kind of problem, plus a reviewer that checks their
  claims.** Lost: it caught 100% of planted mistakes against 95%, at 4 times the cost, with twice
  as many claims on specs that had no planted mistakes, and only 9 of 30 runs ended in a pass.
- **The same reviewer on Opus instead of Sonnet.** Lost: it caught no more (97% against 95%) at
  twice the cost.
- **One reviewer that works in two ways, a full review or a check of corrections only.** Lost:
  an agent asked to check only corrections can slide into reviewing the whole document again,
  which brings back the repeated rounds.
- **Marking findings and corrections inside the document**, as tracked changes in CriticMarkup,
  so a reviewer re-reads only the marked parts. Lost: too much machinery for what it gives. It
  needs editing tools that enforce the markup and a step that strips it before a person signs off,
  and the reviewer cannot write in the document anyway.
- **Review once, correct once, then check only the corrections.**

## Decision Outcome

Chosen option: review once, correct once, then check only the corrections, because in the same
measurement, judged on the document each run ended with, it left as few planted mistakes in it
as the several-reviewers option (3 of 63 each, though that option's reviews had pointed out all
63 along the way), added the
fewest new problems (1.1 per run), ended in a pass in 26 of 30 runs, and cost the least (0.6
times the repeated rounds).

The sequence is fixed:

1. **Review.** The skill's reviewer checks the whole document against the rubric.
2. **Correct.** The drafting agent re-reads the rubric and corrects only what the review report
   lists, once. A decision only the person can make becomes an open question. Suggestions are
   left alone, and nothing else changes. A second measurement showed why the brief must be this
   narrow: without the rubric and "change nothing else", only about half of the corrections
   passed the check.
3. **Correction check.** One correction checker, shared by every skill, checks only that each
   correction was made and that none broke anything. Anything else it notices is a suggestion.
4. A passing check, or a review with no findings, goes to the person. A failing check stops and
   shows the person, rather than correcting again.

When the person changes the document afterwards, that starts the sequence again. It is not a
repeated round, because no agent re-reviews its own corrections.

### Consequences

- Good: every review ends with a definite result, at lower cost than before.
- Good: there is no setting to save before the first review.
- Bad: a mistake the single review misses stays in the document; in the measurement, 3 of 63
  planted mistakes were still there at the end.
- Bad: a failed correction check needs the person, where more rounds might have got through
  without them.
- Bad: the check is not perfect. Documents still ended with about one problem per run that a
  correction had introduced and the check let through.

### Confirmation

Applies to: any skill that has a document reviewed before a person sees it.
Checked by: tests. Each skill's evals check that a document is reviewed at most once between two
messages from the person, corrected at most once, and that every correction is followed by a
correction check. A test with a stand-in checker that always fails checks that the skill stops
and shows the person, and does not review or correct again.
