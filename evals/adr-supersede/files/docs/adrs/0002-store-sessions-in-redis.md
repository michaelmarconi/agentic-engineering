---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: 📝 Draft
date: 2026-10-20
supersedes: 0001
---

# Store sessions in Redis

## Context and Problem Statement

Sessions are stored in Postgres, and loading the session is now the most frequent database
query: at peak it is 40% of all queries and adds about 15 ms to every request.

## Considered Options

- Store sessions in Redis: an in-memory store shared by every server, which we already run for
  caching.
- Keep sessions in Postgres: lost because it keeps the load and the delay described above.
- Signed cookies holding the whole session: lost because a session cannot be ended from the
  server, for example when an account is locked.

## Decision Outcome

Chosen option: store sessions in Redis, because it takes session reads off the database, adds
under 1 ms per request in our load test, and lets the server end a session at once.

### Consequences

- Good: database load falls and requests get faster.
- Bad: sessions are lost if Redis loses its data, so everyone would have to log in again.
- Bad: existing sessions are not copied across, so everyone logs in once more on the day of
  the switch.

### Confirmation

Applies to: any code that stores or reads session data.
Checked by: inspection that sessions are read and written only through Redis, and that nothing
reads the old sessions table.
