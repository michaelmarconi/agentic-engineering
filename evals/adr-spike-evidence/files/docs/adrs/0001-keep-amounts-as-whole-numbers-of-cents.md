---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
---

# 0001. Keep amounts as whole numbers of cents

## Question

In what form does the ledger keep amounts of money?

## Decision

Chosen: keep every amount as a whole number of cents, because floating-point sums drift by
fractions of a cent.

## Background

The ledger adds up thousands of amounts each month, and must never be a cent out.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Whole numbers of cents | Chosen | Sums are exact |
| Floating-point numbers | Rejected | Sums drift by fractions of a cent |

## Consequences

- Good: sums are exact.
- Bad: every amount read from a file must be converted.

## Out of scope

None.

## How we'll check

Applies to: any code that stores or adds up amounts.

1. A test sums 10,000 amounts of 0.10 and expects exactly 100000 cents.

## Open questions

None.

## Technical detail

None.
