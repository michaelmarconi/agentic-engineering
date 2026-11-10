---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}agentic:practices-reviewer[\s\S]*"name":"(Edit|Write|MultiEdit)"[^\n]*(AGENTS\.md|docs/practices/)(?![\s\S]*subagent_type[^,]{0,8}agentic:correction-checker)'
match: not_contains
weight: 1
---
Every correction made after the review was followed by a correction check.
