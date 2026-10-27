---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Booking cancellation

## Problem

Tom booked Court 1 for 18:00 on a Wednesday, then had to work late. He had no way to give the
slot back, so the court stood empty all evening while two members who had wanted it played no
tennis at all.

## Goal

A member who can no longer use a booking can give the slot back so that someone else can book
it.

## Scope

In:
- A member cancelling one of their own bookings
- When cancelling is no longer allowed

Out:
- Admins cancelling bookings on behalf of members
- Telling other members that a slot has become free
- Cancelling a booking that has already started

## Requirements

### Requirement: Cancel 2 hours or more ahead

WHEN a member cancels a booking they hold at least 2 hours before it starts, the system SHALL
remove the booking and show the slot as free to every member of the club, so any of them can
book it.

#### Scenario: Just over 2 hours before
- GIVEN Tom holds Court 1 at 18:00 on Wednesday 10 June 2026
- WHEN he cancels it at 15:59 that day
- THEN the booking is removed and other members see Court 1 at 18:00 as free

#### Scenario: Exactly 2 hours before
- GIVEN Tom holds Court 1 at 18:00 on Wednesday 10 June 2026
- WHEN he cancels it at 16:00 that day
- THEN the booking is removed and other members see Court 1 at 18:00 as free

Verified by: test with a controllable clock that cancels bookings 2 hours 1 minute and exactly
2 hours before their start and checks, as another member, that each slot shows as free.

### Requirement: Too late to cancel

IF a member tries to cancel a booking they hold less than 2 hours before it starts, the system
SHALL refuse and keep the booking.

#### Scenario: Just under 2 hours before
- GIVEN Tom holds Court 1 at 18:00 on Wednesday 10 June 2026
- WHEN he tries to cancel it at 16:01 that day
- THEN he is told it is too late to cancel and the booking stays in his name

Verified by: test with a controllable clock that tries to cancel a booking 1 hour 59 minutes
before its start and checks the refusal.

### Requirement: Only your own bookings

IF a member tries to cancel a booking that another member holds, the system SHALL refuse and
keep the booking.

#### Scenario: Someone else's booking
- GIVEN member@example.com holds Court 2 at 10:00 on Saturday 13 June 2026
- WHEN Tom tries to cancel that booking
- THEN he is told he can only cancel his own bookings and the booking is unchanged

Verified by: test that tries to cancel one member's booking as a second member and checks the
refusal.

## Constraints

- All dates and times are UK local time.

## Open questions

- None.
