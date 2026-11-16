---
type: regex
target: trace
pattern: 'build-reviewer|Run /code-review|Run /security-review|build-correction-checker'
match: not_contains
weight: 1
---
No review or correction check was started.
