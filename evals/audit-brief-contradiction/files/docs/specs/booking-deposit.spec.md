---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: 👍 Accepted
date: 2026-09-01
---

# Booking deposit

## Story

When a customer books a repair slot, the mechanic wants a deposit paid by card, so they can stop losing slots to people who never turn up.

## In scope

- What the requirements below say.

## Out of scope

- Anything else.

## Requirements

### 1. Deposit taken at booking

When a customer books a repair slot, the system SHALL take a deposit of £20 by card before the slot is confirmed.

| Example | Deposit taken at booking |
|---|---|
| Given | a free slot on Tuesday at 10:00 |
| When | a customer books it and pays £20 by card |
| Then | the slot is confirmed |

#### How we'll check

An automated test.

### 2. No deposit, no slot

If the card payment fails, then the system SHALL leave the slot free.

| Example | No deposit, no slot |
|---|---|
| Given | a free slot on Tuesday at 10:00 |
| When | a customer's card is declined |
| Then | the slot stays free |

#### How we'll check

An automated test.

## Constraints

- None.

## Open questions

None.
