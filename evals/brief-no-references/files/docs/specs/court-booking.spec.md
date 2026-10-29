---
status: 📝 Draft
---

# Court booking

## Problem

Members who live far from the club cannot see which courts are free without driving there.

## Goal

A member can see which courts are free and book one from home.

## Scope

In:
- Booking a free court for one hour

Out:
- Booking for guests

## Requirements

### Requirement: Book a free court

WHEN a member books a court for an hour that is free, the system SHALL record the booking for
that member.

#### Scenario: Free court
- GIVEN court 2 is free at 18:00 on Friday
- WHEN a member books court 2 for 18:00 on Friday
- THEN the booking is recorded for that member

Verified by: an integration test of the booking flow.

## Constraints

- None.

## Open questions

- None.
