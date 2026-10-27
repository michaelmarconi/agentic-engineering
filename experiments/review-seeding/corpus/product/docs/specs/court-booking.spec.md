---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Court booking

## Problem

Tom, a member of a four-court club who lives a twenty-minute drive away, goes to the
clubhouse on Sunday evening to write his name on the paper sheet for the next Saturday
morning. Most weeks every Saturday slot is already taken, mostly by members who live next to
the club and pass the sheet every day.

## Goal

Every member can book a court from wherever they are, on the same terms as everyone else.

## Scope

In:
- The slots each court offers
- A member booking a slot for themselves
- The reasons a booking is refused

Out:
- Cancelling a booking
- Admins booking courts on behalf of members
- Bringing guests

## Requirements

### Requirement: Slot times

The system SHALL offer slots on each court that last one hour and start on the hour, the first
at 07:00 and the last at 21:00.

#### Scenario: One day on one court
- GIVEN the club has a Court 1
- WHEN Tom looks at Court 1 for Saturday 6 June 2026
- THEN he sees 15 slots, starting at 07:00, 08:00 and so on up to 21:00, and none at 06:00 or
  22:00

Verified by: test that lists the slots of one court for one day and checks there are exactly
the 15 slots from 07:00 to 21:00.

### Requirement: Make a booking

WHEN a member books a slot that no booking holds and that none of the refusals below applies
to, the system SHALL record the booking in their name and show the slot as taken to every
member of the club.

#### Scenario: Free slot
- GIVEN Court 2 at 09:00 on Saturday 6 June 2026 is free and Tom holds no upcoming bookings
- WHEN Tom books it on Thursday 4 June 2026
- THEN the booking is in Tom's name and other members see the slot as taken

Verified by: test that books a free slot as one member and checks, as a second member, that
the slot shows as taken.

### Requirement: Slot already taken

IF a member tries to book a slot that a booking already holds, the system SHALL refuse the
booking and say the slot is taken.

#### Scenario: Taken by someone else
- GIVEN member@example.com holds Court 2 at 09:00 on Saturday 6 June 2026
- WHEN Tom tries to book Court 2 at 09:00 that day
- THEN he is told the slot is taken and the booking stays with member@example.com

Verified by: test that books a slot as one member, tries the same slot as a second member and
checks the refusal and that the first booking is unchanged.

### Requirement: Slots already started

IF a member tries to book a slot whose start time has passed, the system SHALL refuse the
booking.

#### Scenario: Half an hour late
- GIVEN it is 10:30 on Thursday 4 June 2026 and Court 1 at 10:00 that day has no booking
- WHEN Tom tries to book Court 1 at 10:00 that day
- THEN he is told the slot has already started and no booking is made

#### Scenario: Next slot
- GIVEN it is 10:30 on Thursday 4 June 2026 and Court 1 at 11:00 that day has no booking
- WHEN Tom books Court 1 at 11:00 that day
- THEN the booking is made

Verified by: test with a controllable clock set to 10:30 that tries the 10:00 and 11:00 slots
of a free court.

### Requirement: Booking window

IF a member tries to book a slot that starts more than 14 days from now, the system SHALL
refuse the booking and say when the slot opens for booking.

#### Scenario: Just inside the window
- GIVEN it is 10:00 on Thursday 4 June 2026
- WHEN Tom books a free slot at 09:00 on Thursday 18 June 2026, 13 days and 23 hours ahead
- THEN the booking is made

#### Scenario: Just outside the window
- GIVEN it is 10:00 on Thursday 4 June 2026
- WHEN Tom tries to book a free slot at 11:00 on Thursday 18 June 2026, 14 days and 1 hour ahead
- THEN he is told the slot opens for booking at 11:00 on Thursday 4 June 2026 and no booking
  is made

Verified by: test with a controllable clock that tries free slots 13 days 23 hours and 14 days
1 hour ahead.

### Requirement: Upcoming booking limit

IF a member who holds 3 bookings that have not yet started tries to book another slot, the
system SHALL refuse the booking and say they already hold 3 upcoming bookings.

#### Scenario: Third booking
- GIVEN Tom holds 2 bookings that have not yet started
- WHEN he books a free slot within the booking window
- THEN the booking is made and he holds 3

#### Scenario: Fourth booking
- GIVEN Tom holds 3 bookings that have not yet started
- WHEN he tries to book a free slot within the booking window
- THEN he is told he already holds 3 upcoming bookings and no booking is made

Verified by: test that books three free slots as one member, then tries a fourth and checks
the refusal.

### Requirement: Two courts at once

IF a member tries to book a slot that starts at the same time as a booking they already hold
on another court, the system SHALL refuse the booking.

#### Scenario: Same hour, other court
- GIVEN Tom holds Court 1 at 18:00 on Friday 5 June 2026
- WHEN he tries to book Court 3 at 18:00 that day
- THEN he is told he already has a court at that time and no booking is made

Verified by: test that books one court as a member and then tries another court at the same
start time.

## Constraints

- All dates and times are UK local time.

## Open questions

- None.
