---
status: Draft
date: 2026-10-28
---

# Accept a change only when its automated tests pass on every supported AI model

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. Its skills run on
whichever model the person's session uses, and the same skill can behave differently on
different models. In our own tests, a skill whose cases all passed on Sonnet, Anthropic's
mid-sized model, still failed one on Opus, its largest. Each skill has automated tests, called
evals, which run Claude with the plugin on sample conversations and grade what it did.

We need a rule for which models a change must be tested on before it reaches the main branch,
and so which models we can tell people the plugin works on. This records a decision made on
2026-10-27, while the first skills were being tested.

## Considered Options

- **Test on one model only.** Rejected: it misses failures that appear only on another model,
  such as the one above, and people would meet them first.
- **Test on every model Anthropic offers.** Rejected: each extra model adds the full cost of a
  test run, including for models nobody uses with the plugin.
- **Keep a list of supported models in the README, and merge a change only when the tests of
  every skill it affects pass on each model listed.** Chosen, below.

## Decision Outcome

Chosen option: a list of supported models in the README, with a change merged only when the
tests of every skill it affects pass on each of them, because people can then rely on the plugin
on any listed model, and the cost grows only with the models we choose to support. A change
affects a skill when it alters the skill itself, its reviewer or anything they read. A model
joins the list only once every skill's tests pass on it.

### Consequences

- Good: the README's list is a promise backed by test results.
- Good: a model is added only after the tests have been run on it.
- Bad: each supported model multiplies the cost and time of testing a change.
- Bad: a change can be held back by a failure on one model while it passes on the others.

### Confirmation

Applies to: every change that alters a skill, its reviewer or anything they read.
Checked by: inspection. Before merging, the test cases of every skill the change affects are run
on each model the README lists, each case as many times as it is set to run, and the results show
every case passing on each.
