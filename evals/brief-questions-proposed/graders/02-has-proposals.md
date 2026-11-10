---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '^## Open questions\s[\s\S]*Proposed:'
flags: m
weight: 1
---
Open questions holds at least one proposed answer.
