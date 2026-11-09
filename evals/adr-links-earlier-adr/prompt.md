---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Write an ADR choosing the tool that fills the local database from the remote service. It builds on ADR 0001. We've picked a nightly cron job that downloads the supplier's full export and swaps the SQLite file in one step, rather than fetching products on a cache miss, which would still make pages wait on the supplier. Record it at docs/adrs/0002-catalogue-copy-refresh.md. Don't ask me anything.
