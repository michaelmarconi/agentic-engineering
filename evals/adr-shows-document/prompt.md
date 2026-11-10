---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Record our decision as docs/adrs/0001-session-data-storage.md. Login sessions live in each web server's memory, so people get logged out whenever they reach another server or we deploy. We're moving them to Redis, which we already run for caching. We ruled out Postgres, because it adds a query to every request, and signed cookies, because we can't end a session from the server when we lock an account. How it's set up: Redis runs with `appendonly yes` and `appendfsync everysec` so a restart loses at most a second of sessions, and `maxmemory-policy noeviction` so it never drops a live session; each session is stored under the key `sess:<session id>` with a time-to-live of 1209600 seconds, two weeks. We'll check in code review that session data only goes through Redis. Don't ask me anything.
