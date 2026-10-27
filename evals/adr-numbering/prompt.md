---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Record a decision: we'll send all email through a queue with a separate worker instead of sending it during the web request, because a slow email provider makes pages take up to 20 seconds. We considered sending in the request (too slow when the provider is slow) and a background thread in the web process (emails lost on restart). Don't ask me anything; I'll read it after.
