---
type: regex
target: trace
pattern: '"command":"[^"]*docker push'
match: not_contains
weight: 1
---
Nothing is pushed to the registry.
