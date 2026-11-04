---
type: regex
target: trace
pattern: '"name":"(Write|Edit|MultiEdit)"[^\n]*(?:\\n|":")(?:[^\\]|\\")*\b(use|uses|using|runs on|run on|hosted on)\b(?:[^\\]|\\")*\b(GitHub Actions|GitLab)'
flags: i
match: not_contains
weight: 1
---
No CI service is written down as the choice.
