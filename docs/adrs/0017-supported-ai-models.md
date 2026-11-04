---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
date: 2026-11-04
supersedes: 0008
---

# Support and test the plugin on Opus only

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. Its skills run on
whichever model the person's session uses, and the same skill can behave differently on different
models. Each skill has automated tests, called evals, which run Claude with the plugin on sample
conversations and grade what it did. Each eval run is a billed model run, so every model we test
on adds the full cost and time of a test run to each change.

ADR 0008 keeps a list of supported models in the README, merges a change only when its evals pass
on each model listed, and starts the list with Sonnet, Anthropic's mid-sized model, and Opus, its
largest. It rejected testing on one model only, because a failure that appears only on another
model would reach people first. Since 2026-11-04 the README lists Opus alone, and changes are
tested on Opus only, which goes against that rejection. We need a decision that matches how the
plugin is tested now.

## Considered Options

- **Keep testing on Sonnet and Opus.** Rejected: the maintainer does not use the plugin on
  Sonnet and sees it as outdated next to Opus, so a second test run on every change costs time
  and money for a model nobody we know of relies on.
- **Test on every model Anthropic offers.** Rejected: each extra model adds the full cost of a test
  run, including for models nobody uses with the plugin.
- **List Opus as the only supported model in the README, and merge a change only when the tests
  of every skill it affects pass on Opus.** Chosen, below.

## Decision Outcome

Chosen option: Opus as the only supported model, because it is the model the plugin is used on,
and testing one model halves the cost and time of checking each change. Sonnet can be added back
later, under the rule below, if people need it. A change
affects a skill when it alters the skill itself, its reviewer (the separate agent that checks what
the skill writes) or anything they read. Another model joins the list only once every skill's
tests pass on it, and the maintainer decides when that happens. This decision does not cover the
reviewers, which run on Sonnet as ADR 0007 sets, nor the model that grades the eval runs, which is
also Sonnet.

### Consequences

- Good: each change costs one model's test run, not two.
- Good: the README's list is still a promise backed by test results.
- Bad: a failure that appears only on another model, such as Sonnet, is not caught before
  release, and people using that model may meet it first.
- Bad: adding a model back later means running every skill's tests on it first.

### Confirmation

Applies to: every change that alters a skill, its reviewer or anything they read.
Checked by: inspection. The README names Opus as the only tested model. Before merging, the test
cases of every skill the change affects are run on Opus, each case as many times as it is set to
run, and the results show every case passing. Before a model is added to the list, every skill's
test cases are run on it, and the results show every case passing.

## Open questions

- None.
