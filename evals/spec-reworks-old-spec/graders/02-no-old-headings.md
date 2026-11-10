---
type: regex
target: { source: file, path: docs/specs/word-count.spec.md }
pattern: '^(### Requirement:|#### Scenario:|Verified by:|## Problem|## Goal|## Scope)'
flags: m
match: not_contains
weight: 1
---
No heading or line of the old layout is left.
