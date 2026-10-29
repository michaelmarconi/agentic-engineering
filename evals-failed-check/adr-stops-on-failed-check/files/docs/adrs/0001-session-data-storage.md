---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
date: 2026-10-20
---

# Store sessions in Redis

## Context and Problem Statement

Sessions live in the web server's memory, so every deploy logs everyone out and a second server
can't see sessions made on the first. Redis is clearly the best place for them, since it is fast
and we already know it.

## Considered Options

- Keep sessions in the web server's memory: every deploy logs everyone out, and sessions can't be
  shared between servers.
- Store sessions in Postgres.
- Store sessions in Redis.

## Decision Outcome

Chosen option: Store sessions in Redis, because reads take under a millisecond and expired
sessions disappear on their own.

### Consequences

- Good: deploys no longer log people out, and any server can read any session.
- Bad: one more service to run and watch.

### Confirmation

Applies to: `src/session/store.ts` and `src/session/middleware.ts`.
Checked by: a test that starts two servers against one Redis and reads on one a session made on
the other.

## Open questions

None.
