---
type: regex
target: trace
pattern: '"name":"Write"[^\n]*?"file_path":"[^"]*/scripts?/[^"]*"'
match: not_contains
weight: 1
---
No deploy script is written, since the step needs logic.
