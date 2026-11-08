---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Login sessions live in each web server's memory, so people get logged out whenever the load balancer sends them to another server or we deploy. We could keep them in Postgres, which every server already talks to; in Redis, which we already run for caching; or in signed cookies holding the whole session. I haven't decided which yet. Draft the ADR as docs/adrs/0001-session-data-storage.md so I can think it over.
