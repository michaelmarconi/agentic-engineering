---
type: regex
target: trace
pattern: '"name":"(Write|Edit|MultiEdit)"[^\n]*(?:\\n|":")(?:[^\\]|\\")*`[^`\\]*(pytest|unittest)[^`\\]*`(?!(?:[^\\]|\\")*not set up yet)'
match: not_contains
weight: 1
---
Any test command written, between backticks, has 'not set up yet' on its line.
