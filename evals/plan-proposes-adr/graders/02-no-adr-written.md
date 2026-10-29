---
type: regex
target: trace
pattern: '"name":"(Write|Edit|MultiEdit)","input":\{"file_path":"[^"]*docs/adrs/'
match: not_contains
weight: 1
---
No ADR was written or changed: the person records the ADR.
