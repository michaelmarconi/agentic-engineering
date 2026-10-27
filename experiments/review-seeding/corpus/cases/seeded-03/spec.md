---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Playing partners

## Problem

Jo books a court for her Wednesday doubles four. Her three partners never know which court or
time she got, so each week they ring her to ask. Jo needs an "Add partners" field on the booking
form so the other three names show up next to hers.

## Goal

Everyone can see who is playing on a booking, and partners can see the bookings they are on.

## Scope

In:
- The member who holds a booking adding and removing partners
- A partner leaving a booking

Out:
- Partners who are not members of the club
- Partners cancelling the booking
- Telling partners when the booking is cancelled

## Requirements

### Requirement: Add a partner

WHEN the member who holds a booking adds another member of the club as a partner, the system
SHALL show that partner's name on the booking to every member of the club.

#### Scenario: Doubles partner
- GIVEN Jo holds Court 3 at 19:00 on Wednesday 10 June 2026 with no partners on it
- WHEN she adds member@example.com as a partner
- THEN every member of the club sees member@example.com's name on that booking next to Jo's

Verified by: test that adds a partner as the booking's holder and checks, as a third member,
that the partner's name shows on the booking.

### Requirement: Partner limit

The system SHALL allow at most 3 partners on a booking, and refuse any addition that would
take it past 3.

#### Scenario: Third partner
- GIVEN Jo's booking has 2 partners
- WHEN she adds a third member as a partner
- THEN the booking has 3 partners

#### Scenario: Fourth partner
- GIVEN Jo's booking has 3 partners
- WHEN she tries to add another member as a partner
- THEN she is told a booking can have at most 3 partners and it still has 3

#### Scenario: Two at once
- GIVEN Jo's booking has 2 partners
- WHEN she adds two more members as partners in one go
- THEN both are added and the booking shows its 4 partners

Verified by: test that adds partners to one booking up to and past the limit and checks which
additions are accepted.

### Requirement: Only the holder changes partners

IF a member who does not hold a booking tries to add or remove a partner on it, the system
SHALL refuse and leave the partners unchanged.

#### Scenario: Not the holder
- GIVEN Jo holds Court 3 at 19:00 on Wednesday 10 June 2026 and other@example.com is not on it
- WHEN other@example.com tries to add themselves as a partner
- THEN they are told only Jo can change the partners and the booking is unchanged

Verified by: test that tries to add a partner as a member who does not hold the booking.

### Requirement: Leave a booking

WHEN a partner removes themselves from a booking, the system SHALL take their name off it and
email the member who holds it within 5 minutes.

#### Scenario: Partner drops out
- GIVEN member@example.com is a partner on Jo's booking for Court 3 at 19:00 on 10 June 2026
- WHEN member@example.com removes themselves from it
- THEN their name is off the booking and Jo gets an email saying so within 5 minutes

Verified by: test with a stand-in mail service that removes a partner as that partner and
checks the booking and the captured email.

## Constraints

- All dates and times are UK local time.

## Open questions

- Should the holder be able to add a member who is already a partner on that booking, or
  themselves, and if not, what should they be told?
