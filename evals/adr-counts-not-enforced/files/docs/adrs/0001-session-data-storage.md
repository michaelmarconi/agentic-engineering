---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: 2026-10-20
---

# Store sessions in Redis

## Question

Where do the web servers keep login sessions, so that every server can read them and they survive
a deploy?

## Decision

Chosen: Store sessions in Redis, because every server can reach it and expired sessions disappear
on their own.

## Background

Sessions live in each web server's memory today. So every deploy logs everyone out, and when a second server joins behind the load balancer it cannot see any session that a person started on the first one. We are adding a second server next month to handle evening traffic. So sessions need a home that every server can reach and that survives a deploy.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Keep sessions in the web server's memory | Rejected | Every deploy logs everyone out, and servers can't share sessions |
| Store sessions in Postgres | Rejected | Each request would add a database read, and expired sessions need a clean-up job |
| Store sessions in Redis | Chosen | Fast reads from every server, and expiry is built in |

## Consequences

- Good: deploys no longer log people out, and any server can read any session.
- Bad: one more service to run and watch, and if Redis is not unavailable less often than the servers are not restarted, sessions are not kept no more safely than before.

## Out of scope

None.

## How we'll check

1. A test starts two servers against one Redis and reads on one a session made on the other.
2. A test restarts a server and checks that a session made before the restart still works.

## Open questions

None.

## Technical detail

None.
