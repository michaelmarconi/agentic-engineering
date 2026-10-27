---
type: regex
target: { source: file, path: docs/brief.md }
pattern: 'flutter(?=[\s\S]*\n## Open questions)'
flags: i
match: not_contains
weight: 1
---
Outside Open questions, the brief does not mention Flutter, a technology choice.
