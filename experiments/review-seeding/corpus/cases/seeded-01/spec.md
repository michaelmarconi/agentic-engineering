---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Slot waitlist

## Problem

Ana, a member who works shifts, wants Court 1 at 19:00 on Thursdays, but it is usually booked
within an hour of opening. Twice last month the member holding it cancelled the day before,
and by the time Ana next looked the slot had gone to someone else. She now checks the
timetable six or seven times a day in case a Thursday evening slot comes free.

## Goal

A member who wants a taken slot gets it automatically if it comes free, without having to
keep checking.

## Scope

In:
- A member joining and leaving the waitlist for a slot another member holds
- What happens to a slot with a waitlist when its booking is cancelled

Out:
- Waitlists for slots that are not yet open for booking
- Waiting for "any court" at a given time rather than one slot
- Telling the member who cancelled that the slot went to someone on the waitlist

## Requirements

### Requirement: Join a waitlist

WHEN a member asks to join the waitlist for a slot that another member's booking holds, the
system SHALL add them to the end of that slot's waitlist.

#### Scenario: Second in line
- GIVEN member@example.com is already on the waitlist for Court 1 at 19:00 on Thursday 11 June 2026
- WHEN Ana joins the waitlist for that slot
- THEN she is second on its waitlist, after member@example.com

Verified by: test that adds two members to one slot's waitlist in turn and checks their order.

### Requirement: Waitlists per week

IF a member who is already on the waitlists for 2 slots in a week tries to join the waitlist
for another slot in that week, the system SHALL refuse and say they are already waiting for 2
slots that week.

#### Scenario: Second waitlist in the week
- GIVEN Ana is on the waitlist for Court 1 at 19:00 on Tuesday 9 June 2026 and on no other
- WHEN she joins the waitlist for Court 1 at 19:00 on Thursday 11 June 2026
- THEN she is added to it

#### Scenario: Third waitlist in the week
- GIVEN Ana is on the waitlists for Tuesday 9 June and Thursday 11 June 2026 at 19:00
- WHEN she tries to join the waitlist for Court 2 at 08:00 on Friday 12 June 2026
- THEN she is told she is already waiting for 2 slots that week and is not added

Verified by: test that puts one member on two waitlists in a week and checks that a third in
the same week is refused.

### Requirement: Freed slot goes to the waitlist

WHEN a booking for a slot with a waitlist is cancelled, the system SHALL book the slot for the
first member on the waitlist whom the booking rules allow to book it, email them within 5
minutes, and leave the slot free if the booking rules allow nobody on the waitlist to book it.

#### Scenario: First in line gets it
- GIVEN Ana is first on the waitlist for Court 1 at 19:00 on Thursday 11 June 2026
- WHEN the member holding that slot cancels it on Wednesday 10 June
- THEN the slot is booked in Ana's name and she receives an email saying so within 5 minutes

#### Scenario: First in line already has a court then
- GIVEN Ana is first on the waitlist for that slot and already holds Court 3 at 19:00 that day,
  and member@example.com is second
- WHEN the member holding the slot cancels it
- THEN the slot is booked for member@example.com

Verified by: test with a stand-in mail service that cancels a waitlisted booking and checks
who now holds the slot and that the stand-in received the email within 5 minutes.

### Requirement: Leave a waitlist

WHEN a member leaves a waitlist, the system SHALL remove them from it and keep everyone else
on it in the same order.

#### Scenario: Leaving from the middle
- GIVEN a slot's waitlist is member@example.com, then Ana, then other@example.com
- WHEN Ana leaves it
- THEN the waitlist is member@example.com, then other@example.com

Verified by: test that builds a three-member waitlist, removes the middle member and checks
the order.

## Constraints

- Each slot's waitlist is kept as a first-in, first-out queue stored alongside the slot's
  booking record.

## Open questions

- After a freed slot is booked for someone on its waitlist, who stays on that waitlist,
  including any member skipped because the booking rules did not allow them to book it?
- What should happen when a member asks to join a waitlist they are already on?
