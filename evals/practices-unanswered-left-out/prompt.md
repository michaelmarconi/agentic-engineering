---
tags: [practices]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

/practices testing. We write a failing test before the code it tests. Every change to src/ comes with a test in tests/. Test data lives in tests/data/. A flaky test is fixed or deleted the same day, never skipped. I have no answer on a coverage threshold; leave it out. Don't ask me anything else.
