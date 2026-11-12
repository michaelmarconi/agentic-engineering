---
tags: [spike]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

We plan to have the importer download statements from the bank's website with Python's urllib. Spike whether urllib refuses to download from a site whose certificate has expired, using https://expired.badssl.com/, a public test site kept with an expired certificate for this purpose. Save the record as docs/spikes/2026-11-12-importer-refuses-expired-certificate.md. Just draft it, don't ask me anything.
