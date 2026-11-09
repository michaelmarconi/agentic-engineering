---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Record our decision as docs/adrs/0001-session-data-storage.md. Login sessions live in each web server's memory, so people get logged out whenever they reach another server or we deploy. We're moving them to Redis, which we already run for caching: in our load test a session read took under 1 ms. We ruled out Postgres, because it adds a query to every request, and signed cookies, because we can't end a session from the server when we lock an account. The downside is that if Redis loses its data, everyone logs in again. Two caveats: the load test only covered reads, not Redis failing over to its replica, and how we back Redis up is a separate decision for later. We'll check in code review that session data only goes through Redis. Don't ask me anything.
