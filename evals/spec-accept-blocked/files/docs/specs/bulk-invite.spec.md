---
type: Spec
status: 📝 Draft
---

# Bulk invite

## Problem

Tom runs onboarding for a 40-person team and has to invite each person to the workspace one at
a time, which takes him most of an afternoon.

## Goal

An admin can invite a whole team in one step.

## Scope

In:
- Inviting many people at once by pasting email addresses

Out:
- Importing people from a directory service

## Requirements

### Requirement: Invite many addresses

WHEN an admin submits a list of email addresses, the system SHALL send an invitation to each
valid address that is not already a member.

#### Scenario: One address already a member
- GIVEN first@example.com is already a member
- WHEN an admin submits first@example.com and second@example.com
- THEN only second@example.com receives an invitation

Verified by: an integration test of the invite flow, using a stand-in mail service that records
outgoing invitations.

## Constraints

- None.

## Open questions

- Is there a limit on how many addresses one submission can hold?
- Should invalid addresses block the whole submission or be skipped and reported?
