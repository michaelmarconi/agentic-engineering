---
tags: [spec]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Let's settle the open question on docs/specs/booking-deposit.spec.md: keep to the brief, no deposit and no card payment. A slot is confirmed as soon as it's booked, and a customer who doesn't turn up twice can't book online any more.
