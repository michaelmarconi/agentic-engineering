---
tags: [spec]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Write a spec, saved as docs/specs/auth/account-lockout.spec.md: after 5 failed sign-ins in a row, an account is locked for 15 minutes. Link it to our brief, to the password reset spec (a locked-out person may reset their password instead), and to ADR 0002 at docs/adrs/0002-send-email-through-postmark.md, so readers can see how we send email. Just draft it, no questions.
