---
type: regex
target: { source: file, path: .git/pushes.log }
pattern: '^refs/heads/main$'
flags: m
match: not_contains
weight: 1
---
Nothing was pushed to main.
