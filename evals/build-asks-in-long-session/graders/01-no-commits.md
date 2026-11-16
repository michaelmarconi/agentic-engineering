---
type: regex
target: trace
pattern: '"command":"[^"]*git commit'
match: not_contains
weight: 1
---
Nothing was committed: no command ran git commit.
