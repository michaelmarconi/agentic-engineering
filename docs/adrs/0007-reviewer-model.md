---
status: 👍 Accepted
date: 2026-10-28
---

# Run every agent that checks a document on one fixed AI model

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. Before a person sees
a document the plugin wrote, separate instances of Claude check it: a reviewer reads it against a
list of pass-or-fail checks, a language checker reads its wording, and a correction checker checks
any corrections made after them. Their verdicts decide whether the document goes to the person as
it is or is corrected first, so nothing reaches the person until these checks have passed or the
document has been corrected.

The skills that write documents run on whichever model the person's session uses, which they choose
themselves. Different models judge the same document differently, so if each checker also used the
session's model, the same document could pass for one person and fail for another, and our tests
would have to cover every combination. This records a decision made on 2026-10-27, while the first
skill was being tested.

## Considered Options

- **Checkers use the session's model**, like the skills. Rejected: the pass-or-fail verdicts would
  change with the person's choice of model, and every model would need its own round of testing of
  the checkers.
- **A setting in which the person chooses the checkers' model.** Rejected: a setting has to be
  saved before first use, which our first trial install showed people miss, and it brings back the
  untested combinations.
- **Checkers fixed to Opus**, Anthropic's largest model. Rejected: measured on the same specs, it
  caught about as many deliberately inserted mistakes as Sonnet, its mid-sized model, at twice the
  cost, as ADR 0010 records.
- **Checkers fixed to one exact Sonnet version**, such as Sonnet 5.5. Rejected: Anthropic retires
  old versions, so each pin would stop working in time and has to be updated by hand.
- **Each checker's definition names one model, Sonnet**, by its alias, the short name that always
  points to Anthropic's current Sonnet. Chosen, below.

## Decision Outcome

Chosen option: each checker's definition names Sonnet by its alias, because the checks then judge
every document the same way whatever model the person drafts with, and Sonnet reviews as well as
Opus for half the cost.

### Consequences

- Good: unless someone overrides the checkers' model, the same document gets the same verdict,
  whoever writes it and on whatever model.
- Good: unless someone overrides it, the checkers run on one model. Their verdicts are still tested
  on each supported model the skills run on, as ADR 0008 requires, but never on combinations of
  checker models.
- Bad: when Anthropic moves the alias to a newer Sonnet, the checkers' behaviour changes without
  anyone editing them, and the tests must be run again on it.
- Bad: a person who wants another model for the checkers can only change it for every agent at
  once, through Claude Code's environment settings.

### Confirmation

Applies to: every agent that reviews or checks a document before the person sees it.
Checked by: inspection. Each such agent's definition sets its model to the Sonnet alias, and a
reviewer of any change that adds an agent checks that it does.
