---
type: ADR
status: 👍 Accepted
date: 2026-10-28
---

# Block illegal document status changes with a hook that runs before every file edit

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. The lifecycle it
defines gives documents a status, such as Draft or Ready to build for a spec, the document that
says what one feature must do. A status decides what may happen next: work is planned only from
specs that are Ready to build, and an accepted decision is never edited. Only certain moves are
allowed, and some only by a person.

Claude writes these documents, and a model sometimes slips or is talked out of an instruction.
An illegal move, such as skipping Draft or editing an accepted decision, would quietly undo what
the status promises, so the rules must hold exactly every time. The plugin must not change
anything in the person's repository apart from the documents its skills write. This records a
decision made on 2026-10-26 for specs, and extended to ADRs on 2026-10-27.

## Considered Options

- **Instructions in each skill only.** Rejected: instructions are followed most of the time, not
  every time, and these rules must hold every time.
- **A check in the project's own tooling**, such as a git hook or an automated check run on each
  pull request. Rejected: it means adding files to the person's repository, and it catches a
  mistake only after the edit is made.
- **A hook, a script Claude Code runs automatically, that checks every edit Claude is about to
  make to a lifecycle document and refuses an illegal one.** Chosen, below.

## Decision Outcome

Chosen option: a hook that checks every edit Claude is about to make to a lifecycle document and
refuses an illegal one, because it applies the rules exactly, before the file changes, and needs
nothing in the person's repository.

### Consequences

- Good: Claude cannot make an illegal status move with its file-editing tools, whatever a skill
  or a conversation says.
- Good: the refusal tells Claude why, so it can correct course in the same session.
- Bad: the hook sees only edits made with Claude's file-editing tools, not edits a person makes
  by hand or Claude makes through a shell command.
- Bad: a hook cannot tell whether a person really agreed to a move, such as accepting a
  decision; the skills have to ask.

### Confirmation

Applies to: any change to the status of a lifecycle document, and any edit to a decided ADR.
Checked by: test. Unit tests give the hook examples of edits and check that it allows every legal
status move and refuses every illegal one.
