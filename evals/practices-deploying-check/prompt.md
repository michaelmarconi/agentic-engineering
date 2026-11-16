---
tags: [practices]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent, Bash]
---

/practices deploying. There is one environment, staging, at https://staging.notes.example.test. Only releases from main go there. Deploy with `make deploy ENV=staging` and roll back with `make rollback ENV=staging`. Don't ask me anything.
