---
type: regex
target: trace
pattern: '"name":"(Edit|Write|MultiEdit)"[^\n]*"file_path":\s*"[^"]*CONTRIBUTING\.md"'
match: not_contains
weight: 1
---
CONTRIBUTING.md was not changed.
