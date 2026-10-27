---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '70\s?%(?=[\s\S]*\n## Open questions)'
match: not_contains
weight: 1
---
Outside Open questions, the figure the survey does not support, 70%, is gone.
