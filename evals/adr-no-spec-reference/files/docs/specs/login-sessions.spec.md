---
type: Spec
status: 📝 Draft
---

# Login sessions

## Story

When Priya works across two browser tabs, Priya wants to stay logged in until they log out or are
away for 30 days, so they can keep working without losing what they were typing.

## In scope

- Staying logged in across tabs and visits

## Out of scope

- Logging in from a second device

## Requirements

### 1. Stay logged in

WHILE a person has been active in the last 30 days and has not logged out, the system SHALL keep them logged in.

| Example | Back after 29 days |
|---|---|
| Given | Priya last used the app 29 days ago |
| When | she opens it |
| Then | she is still logged in |

#### How we'll check

Test that ages a session to 29 days and checks it still works.

## Constraints

- None.

## Open questions

- Which store will hold sessions so every server can read them? Proposed: settle it in an ADR.
