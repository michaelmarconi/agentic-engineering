---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: ↪️ Superseded
date: 2026-09-01
---

# Keep amounts as decimal numbers of pounds

## Context and Problem Statement

Amounts need one form throughout the code.

## Considered Options

- The other way: rejected, it was worse.

## Decision Outcome

Chosen option: decimal numbers of pounds, because the clerk thinks in pounds.

### Consequences

- Good: it is simpler.
- Bad: none known.

### Confirmation

Applies to: any code that stores or works out amounts of money.
Checked by: inspection: amounts are floats of pounds.

## Open questions

- None.
