---
type: regex
target: trace
pattern: '"name":"(Write|Edit|MultiEdit)","input":\{"file_path":"[^"]*docs/plans/'
match: not_contains
weight: 1
---
No plan was written.
