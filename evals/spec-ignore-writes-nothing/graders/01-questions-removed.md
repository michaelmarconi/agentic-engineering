---
type: regex
target: { source: file, path: docs/specs/unread-count.spec.md }
pattern: "^## Open questions\\s+None\\.\\s*$"
flags: m
weight: 1
---
Ignoring both questions removes them, leaving Open questions as "None.".
