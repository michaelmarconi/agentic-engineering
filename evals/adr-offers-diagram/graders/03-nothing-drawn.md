---
type: regex
target: { source: file, path: docs/adrs/0001-customs-status-updates.md }
pattern: '```\s*mermaid'
match: not_contains
weight: 1
---
No diagram is written into the ADR before the person picks one.
