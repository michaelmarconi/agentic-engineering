---
tags: [practices]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

/practices reviews and merging. Add these two rules word for word under Rules in the core, not in a topic file:

- Open a pull request only when every spec in it is `👍 Accepted` and every ADR in it is `👍 Accepted` or `❌ Rejected`.
- Never open a pull request from an `/agentic:build` run until its plan is `✅ Built`.

Use the lifecycle's own words and don't explain them: agents read these with the lifecycle page in hand. That's everything for this topic, so don't ask me anything; write them now.
