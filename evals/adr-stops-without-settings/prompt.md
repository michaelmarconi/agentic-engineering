---
tags: [adr]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Record a decision at docs/adrs/0001-send-email-through-a-queue.md: we'll send email through a queue with a separate worker instead of during the web request, because a slow email provider makes pages take up to 20 seconds. We considered sending in the request (too slow) and a background thread in the web process (emails lost on restart). Don't ask me anything.
