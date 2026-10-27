---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Court usage report

## Problem

Sam, treasurer and one of the admins of a four-court club, has to tell the committee whether
Court 4 is used enough to be worth resurfacing this winter. Nobody knows how often each court
is played on, so he scrolled through the timetable day by day and counted bookings for
September by hand, which took a whole evening, and the committee wants a year's figures.

## Goal

Admins can see how much each court was booked in any recent month without counting by hand.

## Scope

In:
- The number of booked slots per court for one month
- Which months an admin can choose
- The order the courts are listed in

Out:
- Usage by individual members
- Usage by time of day or day of the week
- Downloading the report

## Requirements

### Requirement: Booked slots per court

WHEN an admin opens the usage report for a month, the system SHALL show, for each court of the
club, the number of that month's slots on the court that a booking held when the slot started.

#### Scenario: Some bookings cancelled
- GIVEN 40 bookings were made on Court 4 for slots in September 2026, and 3 of them were
  cancelled before they started
- WHEN Sam opens the usage report for September 2026
- THEN Court 4 shows 37 booked slots

#### Scenario: Current month so far
- GIVEN it is 12:00 on Tuesday 27 October 2026, and Court 1 has 20 bookings this month that
  have started and 6 that have not
- WHEN Sam opens the usage report for October 2026
- THEN Court 1 shows 20 booked slots

Verified by: test with a controllable clock that makes and cancels bookings in one month and
checks each court's count.

### Requirement: Months available

WHEN an admin chooses a month for the usage report, the system SHALL show the report for it if
it is the current month or one of the 12 months before the current month.

#### Scenario: Twelve months back
- GIVEN it is Tuesday 27 October 2026
- WHEN Sam chooses October 2025
- THEN he sees the usage report for October 2025

Verified by: test with a controllable clock set to 27 October 2026 that opens the report for
October 2025 and October 2026.

### Requirement: Court order

The system SHALL list the courts in the report from most to fewest booked slots, and courts
with the same number in order of court number.

#### Scenario: Two courts level
- GIVEN in September 2026 Court 1 had 50 booked slots, Court 2 had 37, Court 3 had 50 and
  Court 4 had 12
- WHEN Sam opens the usage report for September 2026
- THEN the courts are listed as Court 1, Court 3, Court 2, Court 4

Verified by: test that committee members can tell at a glance from the report which court is
used least.

### Requirement: Admins only

IF a member who is not an admin tries to open the usage report, the system SHALL refuse.

#### Scenario: Ordinary member
- GIVEN member@example.com is a member of Sam's club but not an admin
- WHEN they try to open the usage report for September 2026
- THEN they are told only admins can see it

Verified by: test that opens the usage report as a member who is not an admin and checks the
refusal.

## Constraints

- All dates and times are UK local time.

## Open questions

- None.
