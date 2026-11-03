---
type: regex
target: { source: file, path: docs/specs/unread-count.spec.md }
pattern: "Verified by: test\\.\\s*$"
flags: m
match: not_contains
weight: 1
---
The bare "Verified by: test." line was fixed.
