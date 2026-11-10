---
type: regex
target: { source: file, path: docs/specs/unread-count.spec.md }
pattern: '^status: 👍️? Accepted\s*\ndate: (?!2026-10-01)\d{4}-\d{2}-\d{2}\s*$'
flags: m
weight: 1
---
The status line changed and, beside it, the date moved on from 2026-10-01 to the day of the change.
