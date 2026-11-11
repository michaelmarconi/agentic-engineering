---
type: regex
target: { source: file, path: docs/specs/appointment-reminders.spec.md }
pattern: '^## Open questions\s*\n(?:(?!^## )[\s\S])*?^### 1\.(?:(?!^## )[\s\S])*?^### 2\.'
flags: m
weight: 1
---
Open questions holds at least two entries.
