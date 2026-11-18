---
type: regex
target: { source: file, path: docs/specs/unread-count.spec.md }
pattern: "(?i)deleted|however old|after some time"
match: not_contains
weight: 1
---
Ignore writes no answer into the spec.
