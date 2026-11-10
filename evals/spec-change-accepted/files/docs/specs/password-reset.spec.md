---
type: Spec
status: 👍 Accepted
---

# Password reset

## Story

When Priya forgets their password on a Monday morning, Priya wants to set a new one themselves,
safely, so they can get back into their account without waiting a day for support to
reply to their email.

## In scope

- Requesting a reset link by email
- Setting a new password from the link

## Out of scope

- Resetting by SMS
- Changing a password while signed in

## Requirements

### 1. Request a reset link

WHEN a person asks to reset the password for an email address, the system SHALL send a link to
that address, from which they can set a new password, if it belongs to an account.

| Example | Known address |
|---|---|
| Given | an account registered to `user@example.com` |
| When | someone requests a reset for `user@example.com` |
| Then | a reset link is emailed to `user@example.com` |
| And | opening the link lets them set a new password and sign in with it |

#### How we'll check

An integration test of the request flow, using a stand-in mail service that records
outgoing messages, which opens the recorded link, sets a new password and signs in with it.

### 2. Reset links expire

WHEN a person opens a reset link, the system SHALL let them set a new password if the link is
at most 24 hours old, and reject the link otherwise.

| Example | Link used just before expiry |
|---|---|
| Given | a reset link issued 23 hours 59 minutes ago |
| When | the person opens it |
| Then | the system lets them set a new password |

| Example | Link used just after expiry |
|---|---|
| Given | a reset link issued 24 hours 1 minute ago |
| When | the person opens it |
| Then | the system rejects the link |

#### How we'll check

Unit tests for both examples.

## Constraints

- None.

## Open questions

- None.
