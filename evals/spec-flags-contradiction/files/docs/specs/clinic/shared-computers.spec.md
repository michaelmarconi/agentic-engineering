---
status: Built
---

# Shared computers

## Problem

Amira, a clinic receptionist, leaves the booking screen signed in at a shared front-desk
computer when she goes to lunch, and anyone walking past can read patients' appointments.

## Goal

An unattended session ends on its own before someone else can use it.

## Scope

In:
- Ending a signed-in session after a period with no activity

Out:
- Signing out by hand
- Limits on how many sessions a person may have

## Requirements

### Requirement: End idle sessions

WHILE a signed-in session has had no activity for 30 minutes, the system SHALL end it and
require the person to sign in again.

#### Scenario: Just under the limit
- GIVEN Amira's last activity was 29 minutes ago
- WHEN she opens the booking screen
- THEN she is still signed in

#### Scenario: Just over the limit
- GIVEN Amira's last activity was 31 minutes ago
- WHEN she opens the booking screen
- THEN she is asked to sign in again

Verified by: test with a controllable clock that checks the session at 29 and 31 minutes of
inactivity.

## Constraints

- None.

## Open questions

- None.
