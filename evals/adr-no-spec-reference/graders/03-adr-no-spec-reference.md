---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: "\\bspecs?\\b|login-sessions"
flags: i
match: not_contains
weight: 1
---
The ADR does not refer to the spec.
