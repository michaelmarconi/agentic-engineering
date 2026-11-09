---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-10-01
---

# Use only Python's standard library

## Question

May the service use packages from outside Python's standard library?

## Decision

Chosen: use only the standard library, because it keeps upkeep low.

## Background

The service is a small Python program that one person maintains. Every outside package must be
kept up to date and checked for security problems, which takes time we do not have.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Use only the standard library | Chosen | No outside packages to keep up to date |
| Use outside packages freely | Rejected | Each one adds upkeep and risk |

## Consequences

- Good: nothing outside Python itself to update.
- Bad: some tasks take more code than a package would need.

## Out of scope

None.

## How we'll check

Applies to: any code in the service.

1. Inspection shows nothing outside the standard library is imported.

## Open questions

None.

## Technical detail

None.
