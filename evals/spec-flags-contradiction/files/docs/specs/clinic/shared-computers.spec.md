---
type: Spec
status: 👍 Accepted
---

# Shared computers

## Story

When Amira, a clinic receptionist, leaves the booking screen signed in at a shared front-desk
computer and goes to lunch, Amira wants the session to end on its own, so no one
walking past can read patients' appointments.

## In scope

- Ending a signed-in session after a period with no activity

## Out of scope

- Signing out by hand
- Limits on how many sessions a person may have

## Requirements

### 1. End idle sessions

WHILE a signed-in session has had no activity for 30 minutes, the system SHALL end it and
require the person to sign in again.

| Example | Just under the limit |
|---|---|
| Given | Amira's last activity was 29 minutes ago |
| When | she opens the booking screen |
| Then | she is still signed in |

| Example | Just over the limit |
|---|---|
| Given | Amira's last activity was 31 minutes ago |
| When | she opens the booking screen |
| Then | she is asked to sign in again |

#### How we'll check

Test with a controllable clock that checks the session at 29 and 31 minutes of
inactivity.

## Constraints

- None.

## Open questions

- None.
