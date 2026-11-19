---
type: regex
target: { source: file, path: docs/specs/unread-count.spec.md }
pattern: "deleted|however old|after some time"
flags: i
match: not_contains
weight: 1
---
Ignore writes no answer into the spec.
