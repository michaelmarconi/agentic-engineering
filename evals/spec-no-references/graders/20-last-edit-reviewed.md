---
type: regex
target: trace
pattern: '"name":"(Edit|Write|MultiEdit)"[^\n]*\.spec\.md(?![\s\S]*subagent_type[^,]{0,8}sdlc:spec-reviewer)'
match: not_contains
weight: 1
---
Every edit to the spec was followed by another review, so the person never gets an unreviewed spec.
