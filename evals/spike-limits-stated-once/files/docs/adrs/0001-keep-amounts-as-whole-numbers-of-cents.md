---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
---

# 0001. Keep amounts as whole numbers of cents

## Context and problem statement

The ledger adds up thousands of amounts each month, and must never be a cent out.

## Considered options

- Whole numbers of cents.
- Floating-point numbers.

## Decision outcome

Chosen option: whole numbers of cents, because floating-point sums drift by fractions of a cent.

### Consequences

- Good, because sums are exact.
- Bad, because every amount read from a file must be converted.

### Confirmation

A test sums 10,000 amounts of 0.10 and expects exactly 100000 cents.

## Open questions

None.
