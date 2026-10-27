---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '\b48\b(?=[\s\S]*\n## Open questions)'
match: not_contains
weight: 1
---
Outside Open questions, the brief does not mention the 48-hour swap expiry, a rule for one capability.
