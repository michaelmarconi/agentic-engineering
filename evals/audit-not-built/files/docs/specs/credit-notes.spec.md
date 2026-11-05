---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
---

# Credit notes

## Problem

Refunds are written as negative invoices, which confuses the accountant.

## Goal

The accounts clerk can rely on what the invoice tool does.

## Scope

In:
- What the requirements below say.

Out:
- Anything else.

## Requirements

### Requirement: Issue a credit note

When the clerk refunds part of an invoice, the system SHALL issue a credit note for that amount, naming the invoice.

#### Scenario: Partial refund
- GIVEN invoice 17 for 1950 cents
- WHEN the clerk refunds 500 cents
- THEN credit note 1 for 500 cents names invoice 17

Verified by: test.

## Constraints

- None.

## Open questions

- Should a credit note get its own number sequence?
