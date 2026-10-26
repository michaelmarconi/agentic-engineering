---
tags: [spec, trigger]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

We chose Postgres over DynamoDB for the event store after last week's spike. Write that decision up as an ADR with the options we considered.
