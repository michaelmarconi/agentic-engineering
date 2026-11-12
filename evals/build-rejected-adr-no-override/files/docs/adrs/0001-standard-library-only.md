---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: ❌ Rejected
date: 2026-11-01
---

# Use only Python's standard library

## Question

May the tool use packages from outside Python's standard library?

## Decision

Chosen: use only the standard library, because the tool then runs wherever Python 3 does.

## Background

The tool must install on a writer's machine by copying one folder, with no package manager.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Use packages from PyPI where they help | Rejected | Each needs an install step |
| Use only the standard library | Chosen | Runs wherever Python 3 does |

## Consequences

- Good: nothing to install but Python.
- Bad: no third-party helpers, even for argument parsing.

## Out of scope

None.

## How we'll check

Applies to: all code under `src/` and `tests/`.

1. Inspection shows every import is from the standard library.

## Open questions

- None.

## Technical detail

None.
