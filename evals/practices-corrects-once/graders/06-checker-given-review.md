---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}sdlc:correction-checker(?![\s\S]*=== REVIEW REPORT ===)'
match: not_contains
weight: 1
---
The correction checker was handed the review report by the relay hook.
