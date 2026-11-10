---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}agentic:correction-checker(?![\s\S]*=== REVIEW REPORT ===)'
match: not_contains
weight: 1
---
The correction checker was handed the review report by the plugin's relay hook, so it checked the corrections against what the reviewer actually found.
