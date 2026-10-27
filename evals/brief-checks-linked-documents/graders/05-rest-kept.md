---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '## Out of scope\s(?:(?!\n## )[\s\S])*Coaching sessions'
weight: 1
---
The brief was changed in place: Out of scope still lists coaching sessions.
