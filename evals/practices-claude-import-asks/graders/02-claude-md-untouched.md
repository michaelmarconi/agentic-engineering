---
type: regex
target: trace
pattern: '"name":"(Edit|Write|MultiEdit)"[^\n]*"file_path":\s*"[^"]*CLAUDE\.md"'
match: not_contains
weight: 1
---
CLAUDE.md was not changed.
