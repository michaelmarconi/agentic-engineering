---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: 👍 Accepted
---

# Overdue reminders

## Problem

Unpaid invoices are forgotten until the firm runs short of cash.

## Goal

The accounts clerk can rely on what the invoice tool does.

## Scope

In:
- What the requirements below say.

Out:
- Anything else.

## Requirements

### Requirement: First reminder

When an invoice is still unpaid 30 days or more after its issue date, the system SHALL put it on the reminder list.

#### Scenario: Thirty days
- GIVEN invoice 17, issued on 1 October and unpaid
- WHEN the list is made on 31 October
- THEN invoice 17 is on it

Verified by: test.

### Requirement: No reminder once paid

The system SHALL leave paid invoices off the reminder list.

#### Scenario: Paid
- GIVEN invoice 18, issued on 1 September and paid
- WHEN the list is made on 31 October
- THEN invoice 18 is not on it

Verified by: test.

### Requirement: Second reminder

When an invoice is still unpaid 60 days or more after its issue date, the system SHALL put it on the second reminder list.

#### Scenario: Sixty days
- GIVEN invoice 19, issued on 1 September and unpaid
- WHEN the second list is made on 31 October
- THEN invoice 19 is on it

Verified by: test.

## Constraints

- None.

## Open questions

- None.
