---
tags: [spec]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Write a spec for refund limits and save it as docs/specs/refund-limits.spec.md. Context: our support agents can refund any order in the shop's admin screen. Last month an agent refunded the same £240 order twice, and the customer also raised a chargeback with their bank, so we paid out three times. We call those ghost refunds, and today they slip through the net until finance reconciles at month end. What we want: the admin screen SHALL refuse a refund that would take the total refunded on an order above what the customer paid, and tell the agent how much can still be refunded. Just draft it, don't ask me anything.
