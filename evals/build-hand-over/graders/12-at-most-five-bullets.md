---
type: regex
target: last_message
pattern: '(?:^[ \t]*(?:[-*+]|\d+[.)])[ \t]+\S[\s\S]*?){6}'
flags: m
match: not_contains
weight: 1
---
The reply has at most five bullets.
