---
type: regex
target: trace
pattern: '"name":"Write","input":\{"file_path":"[^"]*docs/plans/[^"]*","content":"(?:\\.|[^"\\])*```'
match: not_contains
weight: 1
---
The plan written holds no code block.
