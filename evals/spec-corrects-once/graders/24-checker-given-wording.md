---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}sdlc:correction-checker(?![\s\S]*=== WORDING REPORT ===)'
match: not_contains
weight: 1
---
The correction checker was handed the language checker's report by the plugin's relay hook, so it checked the wording corrections too.
