---
type: regex
target: trace
pattern: 'git remote (add|set-head)'
match: not_contains
weight: 1
---
/build did not add a remote or set one up itself.
