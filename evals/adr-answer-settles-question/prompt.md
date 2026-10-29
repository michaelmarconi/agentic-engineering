---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

About the open question in docs/adrs/0003-how-email-is-sent.md: we rejected the background thread because emails waiting in memory are lost whenever the web process restarts, and we deploy several times a day. Don't ask me anything else for now.
