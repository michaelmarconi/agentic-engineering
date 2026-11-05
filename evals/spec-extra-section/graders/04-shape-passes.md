---
type: regex
target: trace
pattern: 'Shape[*\s]*\|[*\s]*fail'
flags: i
match: not_contains
weight: 1
---
The spec reviewer's report does not fail check 1 (Shape) because of the extra section.
