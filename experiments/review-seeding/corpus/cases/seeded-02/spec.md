---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Guest visits

## Problem

Priya, secretary of a four-court club, has to make sure no guest plays at the club more than
3 times in a calendar month, because the club's insurance requires it. Guests sign a book in
the clubhouse, and every Sunday evening Priya goes through the book by hand, often unable to
read the names, and twice this year found out weeks later that a guest had played five times.

## Goal

Admins know which guests played on which booking, and a guest cannot be brought more often
than the club allows.

## Scope

In:
- A member adding a guest to a booking they hold
- The monthly limit on visits by one guest
- Letting the guest see the booking they were added to

Out:
- Guest fees
- Guests booking courts themselves
- Removing a guest from a booking

## Requirements

### Requirement: Add a guest

WHEN a member adds a guest's name and email address to a booking they hold that has no guest
yet, the system SHALL show the guest's name on that booking to the club's admins.

#### Scenario: Guest on a Saturday booking
- GIVEN member@example.com holds Court 2 at 10:00 on Saturday 13 June 2026 with no guest on it
- WHEN that member adds the guest name "Guest One" with guest@example.com
- THEN admins of the club see "Guest One" on that booking

Verified by: test that adds a guest to a booking as its holder and checks, as an admin, that
the guest's name shows on it.

### Requirement: One guest per booking

IF a member tries to add a guest to a booking that already has a guest, the system SHALL
refuse and keep the guest already on it.

#### Scenario: Second guest
- GIVEN member@example.com's booking for Court 2 at 10:00 on Saturday 13 June 2026 has
  guest@example.com on it
- WHEN that member tries to add other.guest@example.com
- THEN they are told the booking already has a guest and guest@example.com stays on it

Verified by: test that adds a guest to a booking and then tries a second one.

### Requirement: Only your own bookings

IF a member tries to add a guest to a booking that another member holds, the system SHALL
refuse.

#### Scenario: Someone else's booking
- GIVEN other@example.com holds Court 1 at 18:00 on Friday 12 June 2026
- WHEN member@example.com tries to add a guest to that booking
- THEN they are told they can only add guests to their own bookings and no guest is added

Verified by: test that tries to add a guest to another member's booking and checks the refusal.

### Requirement: Monthly visits per guest

WHEN a member adds a guest to a booking, the system SHALL accept the guest if their email
address is on fewer than 3 other bookings that start in the same calendar month.

#### Scenario: Third visit in June
- GIVEN guest@example.com is on 2 bookings in June 2026
- WHEN member@example.com adds guest@example.com to their booking on Saturday 27 June 2026
- THEN the guest is added and is now on 3 bookings in June

Verified by: test that adds one guest address to three bookings in the same month and checks
each is accepted.

### Requirement: Guest can see the booking

WHEN a guest is added to a booking, the system SHALL create a guest account for their email
address and email them a link to sign in and see the booking's court, date and time.

#### Scenario: Guest told of the booking
- GIVEN member@example.com holds Court 2 at 10:00 on Saturday 13 June 2026
- WHEN that member adds guest@example.com as their guest
- THEN guest@example.com receives an email with a sign-in link, and after signing in sees
  Court 2, 10:00, Saturday 13 June 2026

Verified by: test with a stand-in mail service that adds a guest, follows the link from the
captured email and checks the booking details shown.

## Constraints

- All dates and times are UK local time.

## Open questions

- None.
