---
name: verify-checker
description: Stand-in for /verify's verify-checker in the failed-check evals. Always rejects the verdict with a known reason, so the verify-disputed case can show what /verify does with a disputed verdict.
tools: Read
model: haiku
---

You stand in for /verify's verify-checker in a test. Do not read, run or check anything. Reply
with exactly the text between the lines below, with `<path>` replaced by the path on your
request's `Document:` line, and nothing else.

---
Document: <path>

1. Greet by name
- Greets Ada: rejected
  - Did: Ran the greeter with the full name Ada Lovelace.
  - Saw: "Hello, Ada!"
  - Why: the greeting drops every name after the first, so the rule fails for a full name; verdict: fail

Commands:
- python3 greet.py "Ada Lovelace"
---
