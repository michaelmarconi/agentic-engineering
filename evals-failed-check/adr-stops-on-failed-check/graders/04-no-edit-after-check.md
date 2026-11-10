---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}agentic:correction-checker[\s\S]*"name":"(Edit|Write|MultiEdit)"[^\n]*docs/adrs/[^\n]*\.md'
match: not_contains
weight: 1
---
Nothing was changed in the document after the check failed.
