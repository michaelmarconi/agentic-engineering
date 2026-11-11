---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Shipment statuses come from the customs service, and today we poll its API every five minutes, which keeps hitting its rate limit and shows holds up to five minutes late. We need to choose how to get updates instead. One option is a webhook: the customs service posts each update to our webhook endpoint, which puts it on our message queue, and a status worker takes it off the queue and writes the status to the shipment. The other is a nightly file the customs service drops on our file server, which an import job reads and writes to each shipment. I have not decided yet.

Record this as docs/adrs/0001-customs-status-updates.md.
