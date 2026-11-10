---
type: regex
target: { source: file, path: docs/specs/unread-count.spec.md }
pattern: "^#### How we'll check\\s*\\n\\s*Test\\.\\s*$"
flags: m
match: not_contains
weight: 1
---
The bare "Test." under How we'll check was fixed.
