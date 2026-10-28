---
status: Draft
date: 2026-10-28
---

# Run every document reviewer on one fixed AI model

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. Before a person
sees a document the plugin wrote, a reviewer checks it: a separate instance of Claude that reads
the document against a list of pass-or-fail checks. The reviewer's verdict decides whether the
document goes to the person as it is or is corrected first, so it acts as a gate.

The skills that write documents run on whichever model the person's session uses, which they
choose themselves. Different models judge the same document differently, so if each reviewer
also used the session's model, the same document could pass for one person and fail for another,
and our tests would have to cover every combination. This records a decision made on 2026-10-27,
while the first skill was being tested.

## Considered Options

- **Reviewers use the session's model**, like the skills. Rejected: the gate would move with the
  person's choice of model, and every model would need its own round of testing of the reviewers.
- **A setting in which the person chooses the reviewers' model.** Rejected: a setting has to be
  saved before first use, which our first trial install showed people miss, and it brings back
  the untested combinations.
- **Reviewers fixed to Opus**, Anthropic's largest model. Rejected: measured on the same specs,
  it caught about as many planted mistakes as Sonnet, its mid-sized model, at twice the cost, as
  ADR 0010 records.
- **Each reviewer's definition names one model, Sonnet**, by its alias, the short name that
  always points to Anthropic's current Sonnet. Chosen, below.

## Decision Outcome

Chosen option: each reviewer's definition names Sonnet by its alias, because the gate then
judges every document the same way whatever model the person drafts with, and Sonnet reviews as
well as Opus for half the cost.

### Consequences

- Good: unless someone overrides the reviewers' model, the same document gets the same verdict,
  whoever writes it and on whatever model.
- Good: the reviewers themselves always run on one model. Their verdicts are still tested on each
  supported model the skills run on, as ADR 0008 requires, but never on combinations of
  reviewer models.
- Bad: when Anthropic moves the alias to a newer Sonnet, the reviewers change under us, and the
  tests must be run again on it.
- Bad: a person who wants another model for the reviewers can only change it for every agent at
  once, through Claude Code's environment settings.

### Confirmation

Applies to: every agent that reviews or checks a document before the person sees it.
Checked by: inspection. Each such agent's definition sets its model to the Sonnet alias, and a
reviewer of any change that adds an agent checks that it does.
