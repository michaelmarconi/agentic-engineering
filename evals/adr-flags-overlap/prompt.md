---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Record a decision at docs/adrs/0003-store-sessions-in-memcached.md: sessions go in Memcached, because our hosting provider runs it for us and we want to stop running Redis ourselves. We also looked at keeping sessions in Postgres, which adds a query to every request. Don't ask me anything you don't need to.
