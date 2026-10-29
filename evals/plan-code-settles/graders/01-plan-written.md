---
type: regex
target: trace
pattern: '"name":"Write","input":\{"file_path":"[^"]*docs/plans/\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md"'
weight: 1
---
A plan was written in docs/plans/, named by its date and title.
