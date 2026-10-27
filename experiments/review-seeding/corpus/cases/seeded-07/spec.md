---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Member removal

## Problem

Priya, secretary of a four-court club, learned in March that a member had left the club, but
he still booked Court 1 twice in April because his account kept working. Stopping it took an
email to Rallybook support and a nine-day wait, and Priya wants to be able to remove him from
the members page herself.

## Goal

When someone leaves the club, an admin can stop them booking courts the same day, and the
courts they had booked go back to other members.

## Scope

In:
- An admin removing a member from their club
- What happens to the removed person's access and upcoming bookings
- Telling the removed person

Out:
- Inviting a removed person back
- Members leaving the club by themselves
- Deleting the removed person's past bookings

## Requirements

### Requirement: Remove a member

WHEN an admin removes a member of their club, the system SHALL end that person's access so
that they can no longer sign in.

#### Scenario: Member who left
- GIVEN member@example.com is a member of Priya's club
- WHEN Priya removes member@example.com
- THEN member@example.com can no longer sign in

#### Scenario: Removing yourself
- GIVEN Priya is the only admin of her club
- WHEN she tries to remove herself
- THEN she is told to make another member an admin first, and she stays a member

Verified by: test that removes a member as an admin and then tries to sign in as that member,
and that tries to remove the club's only admin.

### Requirement: Cancel upcoming bookings

WHEN an admin removes a member, the system SHALL cancel every booking that member holds that
has not started yet and show those slots as free to the club's members.

#### Scenario: Two upcoming bookings
- GIVEN member@example.com holds Court 1 at 18:00 on Friday 12 June 2026 and Court 2 at 10:00
  on Saturday 20 June 2026, and it is now Monday 8 June 2026
- WHEN Priya removes member@example.com
- THEN both slots show as free to other members

Verified by: test with a controllable clock that removes a member holding two future bookings
and checks, as another member, that both slots are free.

### Requirement: Keep near-term bookings

WHEN an admin removes a member, the system SHALL keep each booking of theirs that starts within
the next 48 hours, so that the court is not left empty at short notice.

#### Scenario: Booking tomorrow evening
- GIVEN it is 10:00 on Thursday 11 June 2026 and member@example.com holds Court 1 at 18:00 on
  Friday 12 June 2026, 32 hours away
- WHEN Priya removes member@example.com
- THEN the booking stays and other members still see the slot as taken

Verified by: test with a controllable clock that removes a member holding a booking 32 hours
away and checks the slot still shows as taken.

### Requirement: Tell the removed person

WHEN an admin removes a member, the system SHALL email that person within 5 minutes to say
they are no longer a member of the club on Rallybook.

#### Scenario: Removal email
- GIVEN member@example.com is a member of Priya's club
- WHEN Priya removes member@example.com at 09:00
- THEN member@example.com receives an email by 09:05 saying they are no longer a member

Verified by: test with a stand-in mail service and a controllable clock that removes a member
and checks the captured email and its time.

## Constraints

- Only admins can remove members, and only from their own club.

## Open questions

- None.
