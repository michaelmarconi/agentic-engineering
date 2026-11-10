---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '^## Open questions\s*\n(?:(?!^## )[\s\S])*?^[-*] (?!None\.)(?:(?!Proposed:)[^\n])*(?:\n(?![-*] |## |\n)(?:(?!Proposed:)[^\n])*)*(?:\n(?=[-*] |\n|## )|(?![\s\S]))'
flags: m
match: not_contains
weight: 1
---
No question under Open questions is left bare: each one has "Proposed:".
