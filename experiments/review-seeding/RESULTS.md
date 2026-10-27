# Seeded-defect experiment: linear review rounds vs lenses

Run 2026-10-27. Question: for `/spec` document reviews, does replacing today's linear loop (one
reviewer, fix, review again) with parallel lens reviewers plus a verifier catch more defects?

**Answer: no, not on this corpus.** Today's loop already caught 95% of planted defects, nearly all
in its first round. Lenses reached 100% at 4× the review cost and with about twice as many claims
on clean specs. The decision rule set before the run (at least 15 points more caught, at most 2×
cost, no more false alarms) fails on all three counts. An Opus reviewer did no better than Sonnet.

The experiment points at a different problem: the loop rarely **converges**. Later rounds do not
find planted defects that earlier rounds missed; they find new, smaller gaps and restate decisions
only the person can make, so most runs end at the round cap without a pass.

## Setup

- **Corpus** (`corpus/`): a fictional court-booking app with a brief and 3 clean background specs;
  8 specs with 21 planted defects (12 subtle, 9 obvious) across 10 types, and 2 clean specs.
  Written by a separate agent that never saw the reviewer or lens prompts. The prompts were
  committed before the corpus existed.
- **Arms**, all with a Sonnet fixer and a cap of 3 reviews:
  - **A**: today's `agents/spec-reviewer.md` on Sonnet.
  - **B**: three lenses (`arms/lens-*.md`: Rubric, Consistency, Misreading) in parallel, then a
    verifier (`arms/verifier.md`), all Sonnet.
  - **C**: today's reviewer on Opus.
- 3 runs per spec per arm: 90 runs. A defect counts as caught if a report that reached the fixer
  points it out, judged by Sonnet one defect per call (`score.py`).
- Cost is Claude Code's own per-call estimate at API list prices; read it as relative compute.

## Results

| Measure | A (today) | B (lenses) | C (Opus) |
|---|---|---|---|
| Planted defects caught, all rounds | 95% (60/63) | 100% (63/63) | 97% (61/63) |
| obvious | 93% | 100% | 96% |
| subtle | 97% | 100% | 97% |
| Caught in round 1 | 94% | 98% | 94% |
| Review cost per run (relative to A) | 1× ($0.24) | 4× ($0.96) | 2× ($0.50) |
| Problems claimed on clean specs, round 1 | 1.8 | 3.5 | 3.3 |
| Runs ending in a pass within 3 reviews | 17/30 | 9/30 | 13/30 |

A's 3 misses, each in one run of three: 2 "how, not what" (a design choice left in a
requirement, obvious) and 1 subtle solution in the Problem. C missed that same subtle one and an
unverifiable Verified by line. No arm ever missed a contradiction, ambiguity, unstated outcome or
one-sided limit.

Claims on the clean specs are not all false alarms. For example, A flagged that "90 days" crosses a
clock change and could mean 90 calendar days or 90 × 24 hours, which is a fair point the corpus
author had not planted.

## Limits

- Every planted defect is detectable from the page by design, and the specs are short (40 to 110
  lines). Real misses may be harder, and this measures an upper bound on catch rate.
- One corpus, one author, 3 runs per cell: differences of a few points are within run-to-run noise.
- This tests document reviews only. It says nothing about reviewing multi-file changes to this
  repo, where today's extra rounds were spent.

## What to look at next

Convergence, not recall: why a reviewed and fixed spec keeps failing. From the round-3 reports,
the causes are new edge cases on each pass (suggestions that read as failures), open questions the
person must settle restated as blockers, and gaps the fixer's own edits create.

## Second run: review, fix, confirm

Arm **D** replaces repeated reviews with a fixed sequence: one full review, one fix, then a
confirm check (`arms/confirm.md`) that asks only whether each fix landed and whether any edit broke
something. Anything else it notices is a suggestion. If the confirm check fails, the run stops.

This run also judges the spec each run **ends with** (`score_final.py`): a Sonnet judge per planted
defect (still present, or handled by a fix or an open question), and an Opus judge, a different
model from the Sonnet reviewer and fixer, counting problems the edits introduced.

| Measure | A (today) | B (lenses) | C (Opus) | D (sequence) |
|---|---|---|---|---|
| Planted defects still in the final spec | 5/63 | 3/63 | 6/63 | 3/63 |
| Problems introduced by edits, per run | 1.6 | 2.3 | 1.9 | 1.1 |
| Runs ending in a pass | 17/30 | 9/30 | 13/30 | 26/30 |
| Review cost per run (relative to A) | 1× ($0.24) | 4× ($0.96) | 2× ($0.50) | 0.6× ($0.15) |

**D is as good as or better than every other arm on every measure, at the lowest cost.** It ends
with as few planted defects as lenses, introduces the fewest new problems, and passes 26 of 30
runs. Extra review rounds make things worse, not better: each round brings another fix, and each
fix brings new problems.

The confirm check is not perfect. D's final specs still carry about 1 problem per run that the
edits introduced and the confirm check let through, by the Opus judge's count. Every arm has this;
the fixer, not the reviewer, is now the weakest step. The Opus count is itself a judgement and
includes small points, so read it as relative between arms.

## Reproduce

```
python3 run.py --out results/<name> --runs 3 --jobs 10
python3 score.py --out results/<name>
python3 run.py --out results/<name> --arms D --runs 3 --jobs 10
python3 score_final.py --out results/<name> --arms A,B,C,D
```
