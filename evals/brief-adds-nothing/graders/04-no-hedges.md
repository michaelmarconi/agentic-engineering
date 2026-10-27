---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '\b(probably|likely|presumably|we assume|it is assumed)\b|\[A\]|\[\?\]'
match: not_contains
flags: i
weight: 1
---
The brief has no hedged guesses or inline markers.
