---
type: regex
target: last_message
pattern: '^#{1,3} |=== THE REPORT AS WRITTEN ==='
flags: m
match: not_contains
weight: 1
---
The reply does not paste the report or its sections.
