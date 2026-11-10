---
type: Spec
status: 📝 Draft
---

# Bulk invite

## Story

When onboarding a 40-person team, Tom wants to invite the whole team to the workspace in one
step, so they can spend minutes on it rather than most of an afternoon inviting each person.

## In scope

- Inviting many people at once by pasting email addresses

## Out of scope

- Importing people from a directory service

## Requirements

### 1. Invite many addresses

WHEN an admin submits a list of email addresses, the system SHALL send an invitation to each
valid address that is not already a member.

| Example | One address already a member |
|---|---|
| Given | `first@example.com` is already a member |
| When | an admin submits `first@example.com` and `second@example.com` |
| Then | only `second@example.com` receives an invitation |

#### How we'll check

An integration test of the invite flow, using a stand-in mail service that records
outgoing invitations.

## Constraints

- None.

## Open questions

- Is there a limit on how many addresses one submission can hold? Proposed: 100.
- Should invalid addresses block the whole submission or be skipped and reported? Proposed:
  skipped and reported, so the rest are invited.
