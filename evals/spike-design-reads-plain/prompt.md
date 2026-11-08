---
tags: [spike]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Can our importer read the bank's statement file as the bank sends it? Its code is `read_statement` in src/importer.py, and a sample is in samples/statement.csv. Spike it and save the record as docs/spikes/2026-11-08-importer-reads-bank-file.md. Just draft it, don't ask me anything.
