---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-10-30
---

# Verify the built software separately from the build

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. The
plugin helps a person write a software project's documents and build software from them. Two
different things happen once a piece of work is planned:

- **Building:** writing the code and its tests, and having the result reviewed. This needs only
  the project's files, so it can run on any machine, unattended, with nobody watching.
- **Verifying:** starting the product and using it from the outside, the way a person would, to
  check it does what was asked. This needs a machine that can run the product, which a build
  machine may not be, such as a Linux machine building an app that only runs on a Mac. Some
  checks also need a person to watch.

We need to decide whether the plugin's build step also verifies what it built.

## Considered Options

- **The build step verifies the software before handing it over.** Rejected: a build would then
  need a machine that can run the product, and sometimes a person, so it could no longer run
  anywhere unattended, and its result would depend on where it happened to run.
- **The build step verifies only when the machine it runs on can run the product.** Rejected:
  the same work would be verified on one machine and not on another, so a finished build would
  not say what had been checked without looking up where it ran.
- **Verifying is a separate step after the build.** The build step stops at code, tests and
  reviews and hands the work over. A person then verifies it, on a machine that can run the
  product, before approving the merge.

## Decision Outcome

Chosen option: verifying is a separate step after the build, because each step then runs where
its needs are met: building anywhere, unattended, and verifying where a person and a suitable
machine already are.

### Consequences

- Good: builds can run anywhere, unattended, and every build has checked the same things.
- Good: Claude Code already provides a skill for verifying, `/verify`, so the plugin need not
  provide its own.
- Bad: nobody uses the built software until a person verifies it, and a person can skip it.

### Confirmation

Applies to: what the build step does before it hands work over.
Checked by: inspection. The build step's instructions never start the product.

## Open questions

- None.
