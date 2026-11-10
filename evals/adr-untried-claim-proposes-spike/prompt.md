---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Record our decision as docs/adrs/0001-payment-event-handling.md. Our payment provider tells us about each payment by webhook: created, then paid, then sometimes refunded. We'll handle each webhook as it arrives and update the payment's row straight away. We ruled out a queue that sorts events by time before handling them, because it's another service to run, and asking the provider's API for changes every minute, because customers would wait too long for their receipts. This only works if the provider sends a payment's events in order and never sends "refunded" before "paid": their docs don't say, and none of us has tried it. The downside is that a failed webhook is retried by the provider for up to a day, so a receipt can be late. How we handle card disputes is a separate decision for later. We'll check in code review that webhook handlers never call the provider's API. Don't ask me anything.
