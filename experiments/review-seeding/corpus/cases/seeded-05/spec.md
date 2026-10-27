---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Booking reminders

## Problem

Tom booked Court 2 for 07:00 on a Saturday, twelve days ahead. By the Saturday he had
forgotten about it and slept in, and the court stood empty while two members who had asked for
it at the clubhouse were told it was taken.

## Goal

Members are reminded of each booking a day before it, early enough to play or to give the
slot back.

## Scope

In:
- A reminder email to the member who holds a booking
- Cancelling the booking from the reminder

Out:
- Reminders to partners or guests
- Members choosing when, or whether, they get reminders
- Reminders by any means other than email

## Requirements

### Requirement: Send a reminder

WHEN a booking was made at least 24 hours before it starts, the system SHALL email the member
who holds it a reminder no earlier than 24 hours and no later than 23 hours 55 minutes before
the booking starts.

#### Scenario: Booked well ahead
- GIVEN Tom booked Court 2 at 07:00 on Saturday 6 June 2026 on Wednesday 27 May 2026
- WHEN it is 07:05 on Friday 5 June 2026
- THEN Tom has been sent a reminder for that booking, and not before 07:00

#### Scenario: Booked 25 hours ahead
- GIVEN Tom books Court 2 at 07:00 on Saturday 6 June 2026 at 06:00 on Friday 5 June 2026
- WHEN it is 07:05 on Friday 5 June 2026
- THEN Tom has been sent a reminder for that booking, and not before 07:00

#### Scenario: Booked the same morning
- GIVEN it is 07:00 on Saturday 6 June 2026
- WHEN Tom books Court 2 at 12:00 that day
- THEN Tom is sent the reminder at once

Verified by: test with a controllable clock and a stand-in mail service that makes bookings
at these three times and checks when each reminder reaches the stand-in.

### Requirement: Reminder contents

The system SHALL put in each reminder the court, date and start time of the booking and a link
to cancel it.

#### Scenario: Saturday morning reminder
- GIVEN Tom holds Court 2 at 07:00 on Saturday 6 June 2026
- WHEN his reminder is sent
- THEN it names Court 2, Saturday 6 June 2026 and 07:00, and has a cancel link

Verified by: test with a stand-in mail service that checks a captured reminder's court, date,
time and link.

### Requirement: Cancel from the reminder

WHEN a member opens the cancel link in a reminder, the system SHALL cancel the booking if it
has not started yet, and say that the booking has already started otherwise.

#### Scenario: Cancelled the evening before
- GIVEN Tom holds Court 2 at 07:00 on Saturday 6 June 2026
- WHEN he opens the cancel link at 20:00 on Friday 5 June 2026
- THEN the booking is cancelled

#### Scenario: Link opened after the start
- GIVEN Tom held Court 2 at 07:00 on Saturday 6 June 2026
- WHEN he opens the cancel link at 07:10 that day
- THEN he is told the booking has already started and it stays in his name

Verified by: test with a controllable clock that opens a reminder's cancel link before and
after the booking's start.

### Requirement: No reminder for cancelled bookings

IF a booking is cancelled before its reminder is due, the system SHALL send no reminder for it.

#### Scenario: Cancelled two days before
- GIVEN Tom booked Court 2 at 07:00 on Saturday 6 June 2026 and cancelled it on Thursday 4 June
- WHEN it is 07:00 on Friday 5 June 2026
- THEN no reminder is sent for that booking

Verified by: test with a controllable clock and a stand-in mail service that cancels a booking
before its reminder time and checks no reminder is captured.

## Constraints

- All dates and times are UK local time.
- Reminders are sent by a background job that reads the bookings table once a minute and
  emails every booking whose reminder time has passed.

## Open questions

- None.
