---
tags: [deploy]
max_turns: 40
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent, Bash]
---

Can you write down how we deploy this? We have staging and production; ops/deploy.sh <env> <commit> deploys, ops/check.sh <env> checks it and ops/rollback.sh <env> rolls back.
