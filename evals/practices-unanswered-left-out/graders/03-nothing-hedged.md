---
type: regex
target: trace
pattern: '"name":"(Write|Edit|MultiEdit)"[^\n]*(probably|we assume|\[\?\]|TODO)'
flags: i
match: not_contains
weight: 1
---
No practice is hedged or marked as unsure.
