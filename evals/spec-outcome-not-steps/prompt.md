---
tags: [spec]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Write the spec for changing a password and save it as docs/specs/password-change.spec.md. When someone changes their password we hash the new one, store the hash in the users table, end all their other sessions and email them a notice that it changed. Write it now and flag anything open.
