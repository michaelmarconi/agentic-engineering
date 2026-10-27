---
tags: [adr]
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

We settled the storage questions for the new photo-sharing service in today's call:

- Application data (accounts, albums, comments) goes in Postgres rather than MongoDB, because albums and comments are relational and the team knows Postgres.
- Login sessions go in Redis rather than Postgres, because session reads happen on every request and we already run Redis.
- Uploaded photos go in S3-compatible object storage rather than on the web servers' disks, because the servers are replaced on every deploy.

Write that up as an ADR in docs/adrs/. Don't ask me anything.
