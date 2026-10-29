---
status: 📝 Draft
---

# Login sessions

## Problem

Priya works across two browser tabs, and is logged out of both several times a day, losing what she was typing.

## Goal

People stay logged in until they log out or are away for 30 days.

## Scope

In:
- Staying logged in across tabs and visits

Out:
- Logging in from a second device

## Requirements

### Requirement: Stay logged in

WHILE a person has been active in the last 30 days and has not logged out, the system SHALL keep them logged in.

#### Scenario: Back after 29 days
- GIVEN Priya last used the app 29 days ago
- WHEN she opens it
- THEN she is still logged in

Verified by: test that ages a session to 29 days and checks it still works.

## Constraints

- None.

## Open questions

- Which store will hold sessions so every server can read them?
