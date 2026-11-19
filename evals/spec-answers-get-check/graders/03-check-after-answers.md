---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}agentic:spec-reviewer[\s\S]*"name":"(Edit|Write|MultiEdit)"(?![^\n]*"old_string":"(?:## Open questions|> \*\*Why:\*\*|### \d+\. ))[^\n]*\.spec\.md(?![\s\S]*subagent_type[^,]{0,8}agentic:correction-checker)'
match: not_contains
weight: 1
---
Every change written in after the review, corrections and answers alike, was followed by a check.
