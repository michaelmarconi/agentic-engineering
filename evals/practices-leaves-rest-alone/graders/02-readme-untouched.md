---
type: regex
target: trace
pattern: '"name":"(Edit|Write|MultiEdit)"[^\n]*"file_path":\s*"[^"]*README\.md"'
match: not_contains
weight: 1
---
The README was not changed.
