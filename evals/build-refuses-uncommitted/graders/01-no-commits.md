---
type: regex
target: { source: file, path: .git/commits.log }
pattern: '^=== '
flags: m
match: not_contains
weight: 1
---
Nothing was committed.
