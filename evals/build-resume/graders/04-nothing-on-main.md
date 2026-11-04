---
type: regex
target: { source: file, path: .git/commits.log }
pattern: '^=== main:'
flags: m
match: not_contains
weight: 1
---
No commit was made on main, the default branch.
