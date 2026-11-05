---
type: regex
target: trace
pattern: "Can't find docs/|Error: can't read"
match: not_contains
weight: 1
---
No review agent was refused or reported that it could not read its document.
