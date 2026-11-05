---
type: regex
target: trace
pattern: '"name":"Write","input":\{"file_path":"[^"]*docs/plans/[^"]*","content":"(?:\\.|[^"\\])*Requirement: (?:\\.|[^"\\])*Requirement: '
match: not_contains
weight: 1
---
No plan written names two requirements.
