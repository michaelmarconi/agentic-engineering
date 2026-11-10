---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: ↪️ Superseded
date: 2026-10-20
superseded-by: 0002
---

# Store sessions in Postgres

## Question

Where do the web servers keep logged-in sessions, so every server sees them and they survive a restart?

## Decision

Chosen: store sessions in Postgres, in one shared table every server reads, because every
server already connects to it.

## Background

Logged-in sessions are kept in the memory of each web server, so a person is logged out whenever
their requests reach a different server or a server restarts.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Store sessions in Postgres | Chosen | One shared table, on a database every server already uses |
| Keep sessions in server memory | Rejected | Sessions vanish on restart and are not shared |

## Consequences

- Good: sessions survive restarts and work on every server.
- Bad: every request now makes a database query to load its session.

## Out of scope

None.

## How we'll check

Applies to: any code that stores or reads session data.

1. Inspection shows sessions are read and written only through the sessions table.

## Open questions

None.

## Technical detail

None.
