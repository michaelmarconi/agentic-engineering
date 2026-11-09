---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-10-20
supersedes: 0001
---

# Store sessions in Redis

## Question

Where should the web servers keep login sessions?

## Decision

Chosen: store sessions in Redis, the in-memory store every server shares and we already run for
caching. Redis takes session reads off the database and adds under 1 ms per request in our load
test. The server can still end a session at once.

## Background

[ADR 0001](0001-session-data-storage.md) stores sessions in Postgres. Loading the session is now the most frequent database
query: at peak it is 40% of all queries and adds about 15 ms to every request.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Store sessions in Redis | Chosen | Off the database, under 1 ms per request, and sessions can be ended at once |
| Keep sessions in Postgres | Rejected | Keeps the load and the delay described above |
| Signed cookies holding the whole session | Rejected | A session cannot be ended from the server, for example when an account is locked |

## Consequences

- Good: database load falls and requests get faster.
- Bad: sessions are lost if Redis loses its data, so everyone would have to log in again.
- Bad: existing sessions are not copied across, so everyone logs in once more on the day of the switch.

## Out of scope

None.

## How we'll check

Applies to: any code that stores or reads session data.

1. Inspection shows sessions are read and written only through Redis.
2. Inspection shows nothing reads the old sessions table.

## Open questions

None.

## Technical detail

None.
