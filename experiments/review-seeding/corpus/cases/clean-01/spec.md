---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Booking history

## Problem

Tom plays at his club three or four times a month and splits the cost of new balls with
whoever he played with. At the end of each month he tries to remember which days he played
and on which court, gets it wrong, and twice has paid for balls he did not use.

## Goal

A member can see which courts they played on, and when, over the last few months.

## Scope

In:
- A member seeing their own past bookings from the last 90 days

Out:
- Seeing other members' bookings
- Upcoming bookings
- Bookings older than 90 days
- Downloading or printing the history

## Requirements

### Requirement: List past bookings

WHEN a member opens their booking history, the system SHALL list each booking they held that
has started, started no more than 90 days ago and was not cancelled, with its court, date and
start time.

#### Scenario: Inside and outside 90 days
- GIVEN it is 12:00 on Tuesday 27 October 2026, and Tom held Court 2 at 12:00 on Thursday
  30 July 2026 (89 days ago) and Court 1 at 12:00 on Tuesday 28 July 2026 (91 days ago)
- WHEN Tom opens his booking history
- THEN it lists Court 2, Thursday 30 July 2026, 12:00, and does not list the 28 July booking

#### Scenario: Cancelled booking
- GIVEN Tom booked Court 3 at 18:00 on Friday 2 October 2026 and cancelled it on 1 October
- WHEN Tom opens his booking history
- THEN that booking is not listed

#### Scenario: Booking not yet started
- GIVEN it is 12:00 on Tuesday 27 October 2026 and Tom holds Court 1 at 18:00 that day
- WHEN Tom opens his booking history
- THEN that booking is not listed

Verified by: test with a controllable clock that creates bookings 89 and 91 days back, a
cancelled one and a future one, and checks which appear in the history.

### Requirement: Newest first

The system SHALL list the bookings in a member's history from the most recent start time to
the oldest.

#### Scenario: Three bookings
- GIVEN Tom's history holds bookings that started on 3 October, 20 October and 10 October 2026
- WHEN he opens it
- THEN they are listed as 20 October, 10 October, 3 October

Verified by: test that creates three past bookings out of order and checks the listed order.

### Requirement: Empty history

WHILE a member has no booking that the history would list, the system SHALL show the message
"No bookings in the last 90 days" in place of the list.

#### Scenario: New member
- GIVEN Tom joined the club last week and none of his bookings has started yet
- WHEN he opens his booking history
- THEN he sees "No bookings in the last 90 days"

Verified by: test that opens the history of a member with no past bookings and checks the
message.

## Constraints

- All dates and times are UK local time.

## Open questions

- None.
