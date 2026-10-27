---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Coaching series

## Problem

Priya, the club secretary, runs junior coaching on Court 1 at 18:00 every Tuesday in term time.
Each week she has to remember to book the slot on the day it opens, and twice this year a
member booked it first, so twelve children turned up with nowhere to play.

## Goal

A weekly coaching session holds its court for the whole run of sessions without an admin
booking it again each week.

## Scope

In:
- An admin setting up a weekly series of coaching bookings on one court
- Refusing a series that clashes with existing bookings
- An admin cancelling a series

Out:
- Series set up by members who are not admins
- Changing or cancelling a single session of a series
- Fees for coaching

## Requirements

### Requirement: Set up a series

WHEN an admin sets up a coaching series with a court, a weekday, a start time, a first date
and an end date, the system SHALL book that court at that time on that weekday every week from
the first date until the end date, all at the moment the series is set up, and show each
session to members as "Coaching" rather than in any member's name.

#### Scenario: Autumn term
- GIVEN it is Monday 31 August 2026 and Court 1 has no bookings on Tuesdays at 18:00 this autumn
- WHEN Priya sets up a series on Court 1, Tuesdays at 18:00, from Tuesday 1 September to
  Friday 23 October 2026
- THEN members see Court 1 at 18:00 as "Coaching" on each of the 8 Tuesdays from 1 September
  to 20 October 2026

Verified by: test with a controllable clock that sets up this series and checks, as a member,
which Tuesdays show Court 1 at 18:00 as "Coaching".

### Requirement: Series length

IF an admin sets up a series that would have more than 8 sessions, the system SHALL refuse it.

#### Scenario: Ten weeks
- GIVEN it is Monday 31 August 2026
- WHEN Priya sets up a series on Court 1, Tuesdays at 18:00, from Tuesday 1 September to
  Friday 6 November 2026
- THEN the series is set up with its 10 sessions

Verified by: test that sets up series of 8 and 10 sessions and checks which is accepted.

### Requirement: Clashing bookings

IF any session of a new series falls on a slot that a booking already holds, the system SHALL
refuse the whole series and list the dates that are taken.

#### Scenario: One Tuesday taken
- GIVEN member@example.com holds Court 1 at 18:00 on Tuesday 15 September 2026
- WHEN Priya sets up a series on Court 1, Tuesdays at 18:00, from 1 September to 23 October 2026
- THEN no session is booked and Priya is told 15 September 2026 is taken

Verified by: test that books one slot as a member, sets up a series over it and checks that
no session was booked and the taken date is listed.

### Requirement: Cancel a series

WHEN an admin cancels a series, the system SHALL cancel each of its sessions that has not
started yet and show those slots as free to members.

#### Scenario: Cancelled mid-term
- GIVEN the autumn series has sessions on Tuesdays from 1 September to 20 October 2026
- WHEN Priya cancels the series at 12:00 on Wednesday 30 September 2026
- THEN the sessions from 6 October to 20 October show as free and the earlier ones are unchanged

Verified by: test with a controllable clock that cancels a series part-way through and checks
which slots show as free.

## Constraints

- All dates and times are UK local time.

## Open questions

- None.
