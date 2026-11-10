---
type: ADR
status: 👍 Accepted
date: 2026-10-28
---

# Write automated tests of skills in the layout Claude Code's own test runner expects

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. Its skills are
instructions that Claude follows, so a change to a skill's wording can change what Claude does
in ways nobody notices by reading it. We need repeatable automated tests, which we call evals:
each runs Claude with the plugin on a sample conversation, then grades what it did, either by a
fixed check such as a text match or by a second Claude acting as judge. A useful eval also
shows that the skill made the difference, by running the same conversation without the plugin.

The tests have to load the plugin as a person would get it, with its agents and hooks, in a
throwaway folder, so that a test cannot touch the real repository. This records a decision made
on 2026-10-26, when the first skill's tests were written.

## Considered Options

- **A test runner of our own**, a script that starts Claude Code on each sample conversation and
  checks what it wrote. Rejected: we would have to build and maintain the throwaway folders, the
  grading and the comparison without the plugin ourselves.
- **A general tool for testing prompts against a model.** Rejected: such tools send prompts to a
  model directly, not through Claude Code with the plugin's agents and hooks loaded, so they
  would not test what a person actually runs.
- **The case-folder layout run by `claude plugin eval`**, Claude Code's own command for testing a
  plugin: one folder per test case, holding the conversation, the files to start from and the
  graders. Chosen, below.

## Decision Outcome

Chosen option: the case-folder layout run by `claude plugin eval`, because it loads the real
plugin in a throwaway folder, runs each case several times, compares each run with one without
the plugin, and supports both fixed checks and judges, with nothing for us to maintain.

### Consequences

- Good: a test runs the plugin exactly as Claude Code loads it for a person.
- Good: the comparison without the plugin shows whether a case tests anything at all.
- Bad: the command requires the test cases to sit inside the plugin's folder, so they are copied
  to every person who installs the plugin.
- Bad: we depend on the command's limits, and some behaviours cannot be tested through it.
  For example, a case cannot both let Claude run shell commands and start from saved plugin
  settings.
- Bad: every run of a case is a billed use of the model.

### Confirmation

Applies to: every automated test of a skill's behaviour.
Checked by: demonstration. Running `claude plugin eval` on the plugin finds and runs every test
case.
