---
tags: [practices]
max_turns: 60
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent, Bash]
---

/practices releasing. To release, I run `python3 -m build`, then `git tag v$(cat VERSION)`, then `git push --tags`. Only I release, from main, whenever I like. The version lives in VERSION and I bump it by hand. There are no environments and nothing to roll back. Don't ask me anything.
