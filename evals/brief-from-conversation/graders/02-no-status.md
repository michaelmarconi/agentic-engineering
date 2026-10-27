---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '^status:'
flags: m
match: not_contains
weight: 1
---
The brief has no status line.
