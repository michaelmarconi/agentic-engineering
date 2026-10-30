---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
date: 2026-10-30
---

# Leave running the built software to a separate step

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. The
plugin helps a person write a software project's documents and build from them. Its build skill,
`/build`, takes a plan, a signed-off description of one piece of work, and writes the code, with
tests written first, then has the result reviewed and hands it over for a person to merge. A build
may run unattended on a remote machine, with nobody watching, on a computer that may not be able
to run the product at all, such as a Linux machine building an app that only runs on a Mac.

Claude Code has its own `/verify` skill. It starts the product and uses it from the outside, the
way a person would, to check a change does what was asked, and it saves the steps it used into
the project so they can be repeated. Only a person can start it. We need to decide whether
`/build` also runs the software it built before handing it over.

## Considered Options

- **`/build` starts the software and tries it out itself.** Rejected: it needs a machine that can
  run the product, and sometimes a person to watch, which an unattended remote build does not
  have. It would also repeat a skill Anthropic already maintains.
- **`/build` runs the project's saved `/verify` steps when they exist.** Rejected: only a person
  can start `/verify`, and its steps still need a machine that can run the product, so a build's
  result would depend on where it happened to run.
- **`/build` stops at code, tests and reviews, and a person runs `/verify`.** After `/build` hands
  over, the person runs Claude Code's `/verify` on the result before approving the merge.

## Decision Outcome

Chosen option: `/build` stops at code, tests and reviews, and a person runs `/verify`, because a
build then works the same wherever it runs, and the check that needs the running product happens
where a person and a suitable machine already are.

### Consequences

- Good: builds can run anywhere, unattended.
- Good: the plugin does not own a way of running products that Claude Code already provides.
- Bad: nobody runs the built software until a person does, and a person can skip it.
- Bad: the step depends on Claude Code's `/verify`, which Anthropic may change.

### Confirmation

Applies to: what the build skill does before it hands work over.
Checked by: inspection. The build skill's instructions never start the product or `/verify`.

## Open questions

- None.
