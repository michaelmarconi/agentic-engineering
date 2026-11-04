---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-11-04
---

# Name every changed file in one review request

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. Architecture
decision record (ADR) 0010 has every document a skill writes reviewed once, corrected once, and
then checked by a correction checker. A skill is a set of instructions Claude follows for one
kind of task, such as writing an ADR. The reviewer and the correction checker are agents:
separate instances of Claude, each started with its own instructions and none of the
conversation. The correction checker confirms that each correction does what the review asked.
ADR 0011 has a hook, a script Claude Code runs at set moments, save the document as it was reviewed and hand it, with the review's reports, to the correction checker.
The hook finds the document from the first line of each agent's request, `Document: <path>`,
which names one file.

The plugin's planned `/practices` skill records how a project is set up, tested and released, for
coding agents to follow. One run of it changes two files: a short section of the project's
`AGENTS.md`, and often one longer file on a single topic, such as testing. The section names the
topic file and says when to read it, so the two must agree, and a correction to one can break the
other. The hand-off as it stands can carry only one of them.

## Considered Options

- **Review each file on its own.** Rejected: it runs every review agent twice, and no reviewer
  sees both files together, so a section that names a topic file wrongly could pass both reviews.
- **Copy both files into one temporary file and review that.** Rejected: the review would judge a
  copy the person never sees, and the corrections would have to be copied back into the real
  files.
- **Let the `Document:` line name several files, separated by commas.** The hook saves each file as
  reviewed and hands the checker each one, marked with its path. When the whole line names a file
  that exists, it is read as that one file, even if its name holds a comma, so a line naming one
  file works exactly as today. The hook stops the checker from starting, with a reason Claude
  sees, when the review lacks a report or none of the files has changed since the review.

## Decision Outcome

Chosen option: let the `Document:` line name several files, because one review then sees every
file a run changed, the files the person reads stay the only copies, and every existing skill
keeps working unchanged.

### Consequences

- Good: a reviewer can check that the files agree with each other.
- Good: each review agent runs once for a run, however many files it changed.
- Bad: the hook is more complicated: it must save, compare and hand over several files, and
  treat the same files named in a different order as the same review.
- Bad: the instructions of every review agent must change, so each reads every file named on the
  line and judges them together.
- Bad: many files, or large ones, make a long request for the checker.

### Confirmation

Applies to: any review that covers more than one file.
Checked by: test. Unit tests give the hook requests naming several files and check what it saves,
when it stops the checker from starting, and what it adds to the checker's request; the existing tests check
that a single file works as before.

## Open questions

- None.
