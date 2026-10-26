---
type: llm
weight: 1
---
PASS if the draft's Context section gives a plugin version number (such as "sdlc 0.3.0"), a Claude Code version (a number, or "unknown" if it couldn't be found), and mentions /spec as the skill involved.
FAIL if any of these three is absent from Context.
