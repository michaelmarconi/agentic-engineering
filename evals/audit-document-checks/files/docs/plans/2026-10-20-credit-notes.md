---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Plan
status: 🟢 Ready to build
---

# Issue credit notes

## Specs

- [Credit notes](../specs/credit-notes.spec.md)
  - [Issue a credit note](../specs/credit-notes.spec.md#1-issue-a-credit-note)

## ADRs

| ADR | Decision |
| --- | --- |
| [0002](../adrs/0002-amounts-in-whole-cents.md) | Keep amounts as whole numbers of cents |

## Decisions

- None.

## Plan

Add `credit_note` to `src/invoices.py`, with tests.

## Open questions

- None.
