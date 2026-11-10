---
type: regex
target: { source: file, path: docs/plans/2026-10-28-customs-hold-release.md }
pattern: '^status: 🟢️? Ready to build\s*\ndate: (?!2026-10-28)\d{4}-\d{2}-\d{2}\s*$'
flags: m
weight: 1
---
The status line changed and, beside it, the date moved on from 2026-10-28 to the day of the change.
