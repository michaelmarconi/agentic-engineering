---
type: ADR
status: 👍 Accepted
---

# Keep bookings in PostgreSQL

## Question

Where are bookings stored, so that two members cannot book the same court for the same hour?

## Decision

Chosen: PostgreSQL, because its unique constraints stop double bookings in the database.

## Background

Bookings must be stored so that two members cannot book the same court for the same hour.
