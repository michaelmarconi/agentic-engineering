---
type: regex
target: trace
pattern: '"name":"Write"[^\n]*"file_path":\s*"[^"]*docs/practices/(?!testing\.md")'
match: not_contains
weight: 1
---
No other topic file was written.
