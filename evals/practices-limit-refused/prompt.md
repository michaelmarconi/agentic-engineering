---
tags: [practices]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

/practices hands off. Add these rules to the Rules part of the core, one line each: never edit uv.lock by hand; never run scripts/reset-demo-data.sh; never push to main; never delete anything under tests/data/; never edit .github/workflows/; never change the version in pyproject.toml. Don't ask me anything.
