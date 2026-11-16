---
type: regex
target: trace
pattern: '"name":"(?:Write|Edit|MultiEdit)"'
match: not_contains
weight: 1
---
Nothing is written before the person answers.
