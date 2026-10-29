---
type: regex
target: trace
pattern: '"name":"Write","input":\{"file_path":"[^"]*docs/plans/(?!2026-10-20-customs-hold-release\.md)'
match: not_contains
weight: 1
---
No second plan was written for the same requirement.
