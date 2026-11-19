---
type: regex
target: trace
pattern: '"command":"(?:[^"\\]|\\.)*--accept-open-findings'
match: not_contains
weight: 1
---
The build did not try to accept the open findings.
