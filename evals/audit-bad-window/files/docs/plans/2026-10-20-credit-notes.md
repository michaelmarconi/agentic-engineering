---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to build
---

# Issue credit notes

## Specs

- [Credit notes](../specs/credit-notes.spec.md)
  - Requirement: Issue a credit note

## ADRs

- [0002 Keep amounts as whole numbers of cents](../adrs/0002-amounts-in-whole-cents.md)

## Decisions

- None.

## Plan

Add `credit_note` to `src/invoices.py`, with tests.

## Open questions

- None.
