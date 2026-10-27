---
type: regex
target: { source: file, path: docs/brief.md }
pattern: 'recipe|pantry'
flags: i
match: not_contains
weight: 1
---
Nothing from the README, which describes an old recipe app called Pantry, is in the brief.
