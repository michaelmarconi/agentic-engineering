---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-11-01
---

# Use only Python's standard library

## Context and Problem Statement

The tool must install on a writer's machine by copying one folder, with no package manager.

## Considered Options

- Use packages from PyPI where they help: rejected, because each needs an install step.
- Use only the standard library: chosen.

## Decision Outcome

Chosen option: use only the standard library, because the tool then runs wherever Python 3 does.

### Consequences

- Good: nothing to install but Python.
- Bad: no third-party helpers, even for argument parsing.

### Confirmation

Applies to: all code under `src/` and `tests/`.
Checked by: inspection that every import is from the standard library.

## Open questions

- None.
