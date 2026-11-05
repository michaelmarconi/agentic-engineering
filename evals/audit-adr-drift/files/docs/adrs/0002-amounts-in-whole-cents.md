---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-09-01
supersedes: 0001
---

# Keep amounts as whole numbers of cents

## Context and Problem Statement

Floating-point numbers can't hold most amounts of pounds exactly, so totals drift by a cent.

## Considered Options

- The other way: rejected, it was worse.

## Decision Outcome

Chosen option: whole numbers of cents, because integer sums are exact.

### Consequences

- Good: it is simpler.
- Bad: none known.

### Confirmation

Applies to: any code that stores or works out amounts of money.
Checked by: inspection: every amount is an int of cents; no amount is ever a float, and no code multiplies or divides an amount by a float.

## Open questions

- None.
