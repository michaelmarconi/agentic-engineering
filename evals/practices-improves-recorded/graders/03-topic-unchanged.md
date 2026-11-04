---
type: regex
target: trace
pattern: '"name":"(Edit|Write|MultiEdit)"[^\n]*"file_path":\s*"[^"]*docs/practices/testing\.md"'
match: not_contains
weight: 1
---
The topic file was not changed before the person answered.
