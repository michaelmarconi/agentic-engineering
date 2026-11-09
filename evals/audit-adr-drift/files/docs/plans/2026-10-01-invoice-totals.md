---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Plan
status: ✅ Built
---

# Work out invoice totals

## Specs

- [Invoice totals](../specs/invoice-totals.spec.md)
  - Requirement: Line amount
  - Requirement: Invoice total

## ADRs

- [0002 Keep amounts as whole numbers of cents](../adrs/0002-amounts-in-whole-cents.md)

## Decisions

- None.

## Plan

Add `line_amount` and `total` to `src/invoices.py`, with tests.

## Open questions

- None.
