---
type: regex
target: trace
pattern: '=== END REVIEW REPORT ===(\\n|\n)+=== WORDING REPORT ==='
weight: 1
---
The correction checker was handed the language checker's report by the plugin's relay hook, right after the review report, so it checked the wording corrections too.
