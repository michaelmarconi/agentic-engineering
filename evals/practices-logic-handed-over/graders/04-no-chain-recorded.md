---
type: regex
target: { source: file, path: docs/practices/deploying.md }
pattern: 'docker push'
match: not_contains
weight: 1
---
The deploy commands are not written into the practice as steps.
