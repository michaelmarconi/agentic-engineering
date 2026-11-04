---
type: regex
target: trace
pattern: '"name":"(Write|Edit|MultiEdit)"[^\n]*(?:pytest|unittest)(?![^\n]*not set up yet)'
match: not_contains
weight: 1
---
Any test command written says it is not set up yet.
