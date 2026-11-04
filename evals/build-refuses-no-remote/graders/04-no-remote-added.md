---
type: regex
target: trace
pattern: '"command":"[^"]*git remote (add|set-head)'
match: not_contains
weight: 1
---
/build ran no command that adds or sets up a remote; telling the person to do so is fine.
