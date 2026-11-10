---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}agentic:correction-checker(?![\s\S]*=== END REVIEW REPORT ===(\\n|\n)+=== WORDING REPORT ===)'
match: not_contains
weight: 1
---
If the correction checker ran, the plugin's relay hook handed it the language checker's report right after the review report, so it checked the wording corrections too.
