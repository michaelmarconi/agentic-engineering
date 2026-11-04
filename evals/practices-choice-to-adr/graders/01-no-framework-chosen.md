---
type: regex
target: trace
pattern: '"name":"(Write|Edit|MultiEdit)"[^\n]*(?:\\n|":")(?:[^\\]|\\")*\b(use|uses|using|written with|written in) (pytest|unittest)\b'
flags: i
match: not_contains
weight: 1
---
No test framework is written down as a practice.
