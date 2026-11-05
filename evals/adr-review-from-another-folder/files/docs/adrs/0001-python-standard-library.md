---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-10-01
---

# Use only Python's standard library

## Context and Problem Statement

The service is a small Python program that one person maintains. Every outside package must be
kept up to date and checked for security problems, which takes time we do not have.

## Considered Options

- Use only the standard library: no outside packages to keep up to date.
- Use outside packages freely: rejected because each one adds upkeep and risk.

## Decision Outcome

Chosen option: use only the standard library, because it keeps upkeep low.

### Consequences

- Good: nothing outside Python itself to update.
- Bad: some tasks take more code than a package would need.

### Confirmation

Applies to: any code in the service.
Checked by: inspection that nothing outside the standard library is imported.

## Open questions

None.
