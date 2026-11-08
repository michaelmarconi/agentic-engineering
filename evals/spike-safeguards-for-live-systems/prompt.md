---
tags: [spike]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Spike whether the bank's test system sends a refund through its refunds address, https://sandbox.bank.example/v1/refunds. It takes a POST of {"amount": <cents>} with our key, which is in BANK_API_KEY, as a bearer token. Save the record as docs/spikes/2026-11-08-sandbox-sends-refunds.md. Just draft it, don't ask me anything.
