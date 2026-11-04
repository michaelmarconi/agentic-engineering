---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-11-04
---

# Check the length and imports of recorded practices with a hook

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. Its
planned `/practices` skill, a set of instructions Claude follows for one kind of task, records how a project is set up, tested and released, for coding
agents to follow. It writes a `## Practices` section in the project's `AGENTS.md`, which Claude
reads in full on every task, and longer files on single topics under `docs/practices/`, which it
reads only when a task calls for one. The section is limited to 50 lines and each topic file to
200, and neither may hold a line that starts with `@` followed by a file path, an import, which makes
Claude load that whole file into every session too. Without a check, these files grow a little
with each change until they take up much of what Claude reads on every task, which leaves less
room for the task itself.

Counting lines must be exact, which a model is not. The plugin's skills are tested by running
them on sample conversations, and, as we found when running this plugin's own tests there, a run in
one of Claude Code's cloud sessions cannot be allowed to use shell commands, since that needs an
isolated environment the cloud sessions do not have. So a check that the skill runs as a command could not be tested there.

## Considered Options

- **Leave it to the reviewer agent**, a separate instance of Claude that checks each document the
  skill writes. Rejected: a model counting lines makes mistakes, and the
  limits are meant to hold exactly.
- **A script the skill runs after writing.** Rejected: it holds only when Claude remembers to run
  it, and the skill's tests in cloud sessions could never run it.
- **A hook that checks every edit Claude is about to make to those files.** A hook is a script
  Claude Code runs automatically at set moments, here just before each edit. Like the hook of
  architecture decision record (ADR) 0005, which refuses status changes the lifecycle rules do not allow, it
  refuses an edit that would take the section over 50 lines or a topic file over
  200, or that adds an `@` import, and tells Claude why. It refuses only an edit that makes a
  file longer than the limit and longer than before, so a file already too long can still be
  shortened.

## Decision Outcome

Chosen option: a hook that checks every edit, because it applies the limits exactly, before the
file changes, whatever Claude remembers, and the skill's tests exercise it without running any
command.

### Consequences

- Good: the limits hold for every edit Claude makes to those files, whether or not `/practices` is
  running.
- Good: the refusal says why, so Claude can move detail into a topic file in the same session.
- Bad: the hook sees only edits made with Claude's file-editing tools, not a person's own edits
  or a shell command.
- Bad: a project whose section already runs over 50 lines can still be shortened but can't grow
  through Claude until it is under the limit.

### Confirmation

Applies to: any edit Claude makes to the practices section or the topic files.
Checked by: test. Unit tests give the hook examples of edits and check that it allows each one
within the limits and refuses each one that breaks them. A test of the skill on a sample
conversation, run in a cloud session, has Claude make an edit that breaks a limit and checks that
the edit was refused.

## Open questions

- None.
