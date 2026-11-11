---
type: regex
target: { source: file, path: docs/plans/2026-10-20-customs-hold-release.md }
pattern: '```\s*mermaid'
match: not_contains
weight: 1
---
No diagram is written into the plan before the person picks one.
