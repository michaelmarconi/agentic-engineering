---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: Accepted
date: 2026-10-20
---

# Store sessions in Postgres

## Context and Problem Statement

Logged-in sessions are kept in the memory of each web server, so a person is logged out whenever
their requests reach a different server or a server restarts.

## Considered Options

- Store sessions in Postgres: one shared table every server reads.
- Keep sessions in server memory: rejected because sessions vanish on restart and are not shared.

## Decision Outcome

Chosen option: store sessions in Postgres, because every server already connects to it.

### Consequences

- Good: sessions survive restarts and work on every server.
- Bad: every request now makes a database query to load its session.

### Confirmation

Applies to: any code that stores or reads session data.
Checked by: inspection that sessions are read and written only through the sessions table.
