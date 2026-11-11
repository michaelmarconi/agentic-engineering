---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Shipment statuses come from the customs service, and today we poll its API every five minutes, which keeps hitting its rate limit and shows holds up to five minutes late. We've decided to receive updates by webhook instead: the customs service posts each status update to our webhook endpoint, the endpoint checks the update's signature and puts it on our message queue, and a status worker takes each update off the queue and writes the new status to the shipment. We rejected polling more often, because the rate limit already bites, and a nightly file, because holds would show a day late. The good: holds show within seconds. The bad: the endpoint must be reachable from the internet. We'll check it with an integration test that posts a signed sample update to the endpoint and sees the shipment's status change.

Record this as docs/adrs/0001-customs-status-updates.md.
