---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}agentic:correction-checker(?![\s\S]*=== WORDING REPORT ===)'
match: not_contains
weight: 1
---
If the correction checker ran, the relay hook handed it the wording report.
