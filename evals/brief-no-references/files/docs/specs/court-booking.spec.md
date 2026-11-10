---
type: Spec
status: 📝 Draft
---

# Court booking

## Story

When a member who lives far from the club wants to play, the member wants to see which courts are
free and book one from home, so they can play without driving there to find out.

## In scope

- Booking a free court for one hour

## Out of scope

- Booking for guests

## Requirements

### 1. Book a free court

WHEN a member books a court for an hour that is free, the system SHALL record the booking for
that member.

| Example | Free court |
|---|---|
| Given | court 2 is free at 18:00 on Friday |
| When | a member books court 2 for 18:00 on Friday |
| Then | the booking is recorded for that member |

#### How we'll check

An integration test of the booking flow.

## Constraints

- None.

## Open questions

- None.
