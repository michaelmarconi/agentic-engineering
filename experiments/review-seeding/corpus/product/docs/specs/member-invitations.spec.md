---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
---

# Member invitations

## Problem

Priya, secretary of a four-court club, lets new members book courts by telling them the
club's one shared password. Everyone who has joined in the last five years knows it, so people
who left the club long ago still book courts on Saturday mornings, and Priya cannot tell who
they are.

## Goal

Each person who can book the club's courts has their own account, and only people an admin
chose to let in can get one.

## Scope

In:
- An admin inviting a person to the club by email address
- The invited person creating their account from the invitation

Out:
- Removing a member from the club
- Members inviting other people
- Changing the email address of an existing account

## Requirements

### Requirement: Send an invitation

WHEN an admin invites an email address that does not belong to a member of their club, the
system SHALL email that address a link to create an account at the admin's club.

#### Scenario: New person
- GIVEN Priya is an admin of a club and new@example.com does not belong to any of its members
- WHEN she invites new@example.com
- THEN new@example.com receives an email with a link to create an account at Priya's club

Verified by: test with a stand-in mail service that invites new@example.com and checks the
stand-in received one email to that address containing a link for the inviting club.

### Requirement: Existing member

IF an admin invites an email address that already belongs to a member of their club, the
system SHALL refuse the invitation and say that the person is already a member.

#### Scenario: Already a member
- GIVEN member@example.com belongs to a member of Priya's club
- WHEN Priya invites member@example.com
- THEN no email is sent and Priya is told the person is already a member

Verified by: test with a stand-in mail service that invites an existing member's address and
checks the refusal message and that the stand-in received no email.

### Requirement: Invitation expiry

WHEN a person opens an invitation link, the system SHALL let them create an account if the
invitation was sent at most 7 days earlier, and show that the invitation has expired
otherwise.

#### Scenario: Just inside 7 days
- GIVEN Priya invited new@example.com 6 days and 23 hours ago
- WHEN the person opens the link
- THEN they can create their account

#### Scenario: Just past 7 days
- GIVEN Priya invited new@example.com 7 days and 1 hour ago
- WHEN the person opens the link
- THEN they are told the invitation has expired and no account is created

Verified by: test with a controllable clock that opens one invitation's link 6 days 23 hours
after sending and another's 7 days 1 hour after sending.

### Requirement: One use per invitation

IF a person opens an invitation link that has already been used to create an account, the
system SHALL show that the invitation has already been used and create no account.

#### Scenario: Second use
- GIVEN new@example.com created an account from its invitation yesterday
- WHEN the same link is opened again today
- THEN they are told the invitation has already been used and no second account exists

Verified by: test that creates an account from an invitation link, opens the link again and
checks the message and that the club still has one account for new@example.com.

## Constraints

- Only admins can invite people, and only to their own club.

## Open questions

- None.
