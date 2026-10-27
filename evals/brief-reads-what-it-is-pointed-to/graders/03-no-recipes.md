---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '(?i)recipe'
match: not_contains
weight: 1
---
Nothing from the README's old recipe app is in the brief.
