---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: 👍 Accepted
date: 2026-09-01
---

# Closed days

## Story

When the shop is shut for a day, the mechanic wants that day closed to bookings, so no customer turns up to a locked door.

## In scope

- What the requirements below say.

## Out of scope

- Anything else.

## Requirements

### 1. Closing a day

When the mechanic marks a day as closed, the system SHALL offer no slots on that day.

| Example | Closing a day |
|---|---|
| Given | Friday 12 December has free slots |
| When | the mechanic marks it closed |
| Then | customers see no slots that day |

#### How we'll check

An automated test.

### 2. Bookings already made

When the mechanic marks a day closed that already has bookings, the system SHALL list those bookings for the mechanic.

| Example | Bookings already made |
|---|---|
| Given | two bookings on Friday 12 December |
| When | the mechanic marks it closed |
| Then | both bookings are listed |

#### How we'll check

An automated test.

## Constraints

- None.

## Open questions

None.
