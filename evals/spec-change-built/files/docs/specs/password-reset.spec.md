---
status: Built
---

# Password reset

## Problem

Priya forgets her password on a Monday morning and has no way back into her account except
emailing support, who take a day to reply.

## Goal

People who forget their password can set a new one themselves, safely, in minutes.

## Scope

In:
- Requesting a reset link by email
- Setting a new password from the link

Out:
- Resetting by SMS
- Changing a password while signed in

## Requirements

### Requirement: Request a reset link

WHEN a person asks to reset the password for an email address, the system SHALL send a reset
link to that address if it belongs to an account.

#### Scenario: Known address
- GIVEN an account registered to user@example.com
- WHEN someone requests a reset for user@example.com
- THEN a reset link is emailed to user@example.com

Verified by: an integration test of the request flow, using a stand-in mail service that records
outgoing messages.

### Requirement: Reset links expire

WHEN a person opens a reset link, the system SHALL let them set a new password if the link is
at most 24 hours old, and reject the link otherwise.

#### Scenario: Link used just before expiry
- GIVEN a reset link issued 23 hours 59 minutes ago
- WHEN the person opens it
- THEN the system lets them set a new password

#### Scenario: Link used just after expiry
- GIVEN a reset link issued 24 hours 1 minute ago
- WHEN the person opens it
- THEN the system rejects the link

Verified by: unit tests for both scenarios.

## Constraints

- None.

## Open questions

- None.
