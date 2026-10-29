---
status: 👍 Accepted
---

# Keep bookings in PostgreSQL

## Context and problem statement

Bookings must be stored so that two members cannot book the same court for the same hour.

## Decision outcome

Chosen option: PostgreSQL, because its unique constraints stop double bookings in the database.
