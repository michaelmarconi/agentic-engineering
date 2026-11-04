---
tags: [spike]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Spike two things for the statement import spec: whether our importer can read the bank's file (samples/statement.csv) as it comes, and whether it can import a year of statements, 50,000 transactions, in under a minute.
