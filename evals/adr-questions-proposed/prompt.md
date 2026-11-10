---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Record an ADR at docs/adrs/0001-session-data-storage.md: our web app needs somewhere to keep session data, and we're weighing Redis against keeping it in our existing Postgres database. We haven't chosen. I'm away today, so leave whatever you can't decide as questions.
