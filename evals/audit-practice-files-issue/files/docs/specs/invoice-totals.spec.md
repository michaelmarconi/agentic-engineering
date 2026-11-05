---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
---

# Invoice totals

## Problem

The clerk adds up invoice lines by hand and makes mistakes.

## Goal

The accounts clerk can rely on what the invoice tool does.

## Scope

In:
- What the requirements below say.

Out:
- Anything else.

## Requirements

### Requirement: Line amount

The system SHALL work out each line's amount as its quantity times its unit price.

#### Scenario: Three at a price
- GIVEN a line of 3 hinges at 250 cents each
- WHEN the line's amount is worked out
- THEN it is 750 cents

Verified by: test.

### Requirement: Invoice total

The system SHALL work out an invoice's total as the sum of its lines' amounts.

#### Scenario: Two lines
- GIVEN lines of 750 and 1200 cents
- WHEN the total is worked out
- THEN it is 1950 cents

Verified by: test.

## Constraints

- None.

## Open questions

- None.
