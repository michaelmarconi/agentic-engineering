---
type: regex
target: trace
pattern: 'gh pr create|git merge '
match: not_contains
weight: 1
---
No pull request was opened and nothing was merged.
