---
type: regex
target: trace
pattern: '"name":"(Edit|Write|MultiEdit)"[^\n]*"file_path":\s*"[^"]*AGENTS\.md"'
match: not_contains
weight: 1
---
AGENTS.md was not changed.
