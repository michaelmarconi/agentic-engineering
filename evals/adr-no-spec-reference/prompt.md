---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

We've decided sessions go in Redis, which we already run for caching, rather than Postgres, which would add a query to every request. Record that at docs/adrs/0001-store-sessions-in-redis.md, and add a note in docs/specs/login-sessions.spec.md pointing to the ADR so people know it's settled. Don't ask me anything.
