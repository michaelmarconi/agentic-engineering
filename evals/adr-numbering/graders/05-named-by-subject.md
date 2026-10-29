---
type: regex
target: trace
pattern: '"file_path":"[^"]*docs/adrs/0004-send-'
match: not_contains
weight: 1
---
The new ADR's file name does not state the decision the way its title does, as in 0004-send-email-through-a-queue.md.
