---
type: regex
target: trace
pattern: '"name":"(Write|Edit|MultiEdit)"[^\n]*\b(use|uses|using|with) `?(pytest|unittest)\b'
flags: i
match: not_contains
weight: 1
---
No test framework is written down as a practice.
