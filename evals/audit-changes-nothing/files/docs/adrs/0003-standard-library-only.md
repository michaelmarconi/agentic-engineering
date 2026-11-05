---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-09-01
---

# Use only Python's standard library

## Context and Problem Statement

The tool is run on the clerk's own computer, where nothing can be installed.

## Considered Options

- The other way: rejected, it was worse.

## Decision Outcome

Chosen option: the standard library only, because it needs no install step.

### Consequences

- Good: it is simpler.
- Bad: none known.

### Confirmation

Applies to: all code under `src/`.
Checked by: inspection: every import in `src/` is a module of Python's standard library.

## Open questions

- None.
