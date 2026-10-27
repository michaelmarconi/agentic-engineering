---
tags: [adr]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

I accept docs/adrs/0003-send-email-through-a-queue.md, but first change the Confirmation so it's checked by a test that fails if any code other than the queue worker calls the email provider.
