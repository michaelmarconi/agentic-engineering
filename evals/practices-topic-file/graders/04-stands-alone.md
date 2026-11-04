---
type: regex
target: { source: file, path: docs/practices/testing.md }
pattern: 'CONTRIBUTING|README|docs/practices/'
match: not_contains
weight: 1
---
The topic file refers to no other file the agent must read.
