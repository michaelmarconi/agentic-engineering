---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Club notices

## Problem

When Court 3 was being resurfaced for a week in May, Priya, the club secretary, pinned a note
in the clubhouse. Most members book from home and never saw it, so eleven of them turned up
for bookings on a court they could not play on, and several complained to the committee.

## Goal

Admins can tell every member of the club something for a set period, and members see it when
they next use Rallybook.

## Scope

In:
- An admin posting a notice with an end date
- Members of the club seeing the notices that are current

Out:
- Editing or deleting a notice before its end date
- Emailing notices to members
- Notices that start on a later date than the day they are posted

## Requirements

### Requirement: Show a notice until its end date

WHEN an admin posts a notice with an end date, the system SHALL show it to every member of
that admin's club, and to no one else, who opens Rallybook from the moment it is posted until
midnight at the end of its end date, and not after that.

#### Scenario: Last minutes of the end date
- GIVEN Priya posted a notice with the end date Friday 12 June 2026
- WHEN member@example.com opens Rallybook at 23:58 on Friday 12 June 2026
- THEN they see the notice

#### Scenario: Just after the end date
- GIVEN Priya posted a notice with the end date Friday 12 June 2026
- WHEN member@example.com opens Rallybook at 00:01 on Saturday 13 June 2026
- THEN they do not see the notice

Verified by: test with a controllable clock that opens Rallybook as a member at 23:58 on a
notice's end date and at 00:01 the day after.

### Requirement: Notice length

WHEN an admin posts a notice, the system SHALL accept it if its text is at most 500 characters
long, and refuse it and say the limit otherwise.

#### Scenario: At the limit
- GIVEN Priya has written a notice of exactly 500 characters
- WHEN she posts it
- THEN it is posted

#### Scenario: One over
- GIVEN Priya has written a notice of 501 characters
- WHEN she tries to post it
- THEN she is told notices can be at most 500 characters and it is not posted

Verified by: test that posts notices of 500 and 501 characters and checks which is accepted.

### Requirement: End date not in the past

IF an admin gives a notice an end date before the day it is posted, the system SHALL refuse
it.

#### Scenario: Yesterday's date
- GIVEN it is Wednesday 10 June 2026
- WHEN Priya tries to post a notice with the end date Tuesday 9 June 2026
- THEN she is told the end date has passed and the notice is not posted

#### Scenario: Today's date
- GIVEN it is 09:00 on Wednesday 10 June 2026
- WHEN Priya posts a notice with the end date Wednesday 10 June 2026
- THEN it is posted and members see it until midnight that night

Verified by: test with a controllable clock that posts notices ending yesterday and today.

### Requirement: Newest first

WHILE a club has more than one current notice, the system SHALL show them from the most
recently posted to the oldest.

#### Scenario: Two notices
- GIVEN Priya posted a notice on 1 June 2026 and another on 8 June 2026, both ending 30 June
- WHEN a member opens Rallybook on 10 June 2026
- THEN they see the 8 June notice above the 1 June notice

Verified by: test that posts two notices a week apart and checks their order.

## Constraints

- All dates and times are UK local time.
- Only admins can post notices, and only to their own club.

## Open questions

- None.
