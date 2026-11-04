---
tags: [practices]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Write, Edit]
---

Add these six lines under ### Rules in AGENTS.md, exactly as written, and change nothing else in any file: "- Never edit uv.lock by hand." "- Never run scripts/reset-demo-data.sh." "- Never push to main." "- Never delete anything under tests/data/." "- Never edit .github/workflows/." "- Never change the version in pyproject.toml." If you can't, tell me why and stop.
