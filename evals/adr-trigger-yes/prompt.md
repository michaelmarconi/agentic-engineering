---
tags: [adr, trigger]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

We've decided to use PostgreSQL full-text search for the product catalogue instead of running Elasticsearch, since the catalogue is only 20,000 items and we already run Postgres. Write that decision down.
