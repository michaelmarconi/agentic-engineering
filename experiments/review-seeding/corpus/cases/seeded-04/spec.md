---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# No-shows

## Problem

Members at Priya's club complain that Court 2 often sits empty on Saturday mornings even
though the timetable shows it booked. Priya, the club secretary, walks past the courts most
Saturdays and sees it, but she has no record of whose bookings went unused, so when the
committee asked her which members keep doing it she could only guess.

## Goal

Admins have a record of which members' bookings went unused, and members know when one of
their bookings was recorded that way.

## Scope

In:
- An admin marking a booking as a no-show, and removing that mark
- Telling the member whose booking was marked
- Showing admins how many no-shows each member has had recently

Out:
- Penalties for no-shows, such as stopping a member from booking
- Members disputing a no-show
- Members checking in when they arrive at the court

## Requirements

### Requirement: Mark a no-show

WHEN an admin marks a booking as a no-show, the system SHALL record the mark if the booking's
start time has passed, and refuse it otherwise.

#### Scenario: After the start
- GIVEN member@example.com held Court 2 at 09:00 on Saturday 13 June 2026
- WHEN Priya marks that booking as a no-show at 09:20 that day
- THEN the booking is recorded as a no-show

#### Scenario: Before the start
- GIVEN member@example.com holds Court 2 at 09:00 on Saturday 13 June 2026
- WHEN Priya tries to mark that booking as a no-show at 08:50 that day
- THEN she is told the booking has not started yet and no mark is recorded

Verified by: test with a controllable clock that marks a 09:00 booking at 08:50 and at 09:20.

### Requirement: Only admins mark no-shows

IF a member who is not an admin tries to mark or unmark a booking as a no-show, the system
SHALL refuse.

#### Scenario: Member tries to mark
- GIVEN other@example.com is a member but not an admin
- WHEN they try to mark member@example.com's booking from that morning as a no-show
- THEN they are told only admins can do this and no mark is recorded

Verified by: test that tries to mark a past booking as a no-show as a member who is not an
admin.

### Requirement: Tell the member

WHEN a booking is marked as a no-show, the system SHALL send the member who held it a text
message naming the court, date and start time of that booking.

#### Scenario: Member told
- GIVEN member@example.com held Court 2 at 09:00 on Saturday 13 June 2026
- WHEN Priya marks it as a no-show
- THEN member@example.com receives a text message naming Court 2, 13 June 2026 and 09:00

Verified by: test with a stand-in message service that marks a no-show and checks the
captured message's contents.

### Requirement: No-show count

The system SHALL show admins, for each member, the number of that member's bookings marked as
no-shows that started no more than 90 days ago.

#### Scenario: Old no-show drops off
- GIVEN member@example.com has a no-show on a booking that started 89 days ago and another on
  one that started 91 days ago
- WHEN Priya looks at member@example.com's no-show count
- THEN it shows 1

Verified by: test with a controllable clock that creates no-shows 89 and 91 days back and
checks the count is 1.

### Requirement: Remove a mark

WHEN an admin removes the no-show mark from a booking, the system SHALL promptly stop counting
it in that member's no-show count.

#### Scenario: Mark made by mistake
- GIVEN member@example.com's count is 2 and one of those no-shows was marked by mistake
- WHEN Priya removes that mark
- THEN the count shows 1

Verified by: test that marks two no-shows, removes one mark and checks the count is 1.

## Constraints

- All dates and times are UK local time.

## Open questions

- None.
