---
type: regex
target: trace
pattern: '"name":"Write","input":\{"file_path":"[^"]*docs/plans/[^"]*","content":"(?:\\.|[^"\\])*\[Release recorded\]\([^)]*#2-release-recorded\)(?:\\.|[^"\\])*\[Coordinator emailed on release\]\([^)]*#3-coordinator-emailed-on-release\)'
weight: 1
---
One plan is written naming both requirements.
