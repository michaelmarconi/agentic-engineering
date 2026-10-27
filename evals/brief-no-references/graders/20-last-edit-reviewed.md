---
type: regex
target: trace
pattern: '"name":"(Edit|Write|MultiEdit)"[^\n]*docs/brief\.md(?![\s\S]*subagent_type[^,]{0,8}sdlc:brief-reviewer)'
match: not_contains
weight: 1
---
Every edit to the brief was followed by another review, so the person never gets an unreviewed brief.
