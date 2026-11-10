---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: 👍 Accepted
---

# Invoice export

## Problem

The accountant retypes every invoice into their own software.

## Goal

The accounts clerk can rely on what the invoice tool does.

## Scope

In:
- What the requirements below say.

Out:
- Anything else.

## Requirements

### Requirement: Export as CSV

When the clerk exports invoices, the system SHALL write one CSV row per invoice, after a header row, with the columns number, date and total, in that order, the total in cents.

#### Scenario: One invoice
- GIVEN invoice 17, dated 2026-10-01, totalling 1950 cents
- WHEN the clerk exports
- THEN the file is `number,date,total` then `17,2026-10-01,1950`

Verified by: test.

## Constraints

- None.

## Open questions

- None.
