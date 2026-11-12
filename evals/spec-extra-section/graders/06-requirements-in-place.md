---
type: regex
target: { source: file, path: docs/specs/password-reset.spec.md }
pattern: '^## (?!Requirements|Open questions)[^\n]*\n(?:(?!^## )[\s\S])*^### \d+\. '
flags: m
match: not_contains
weight: 1
---
Every requirement is still under Requirements: no other section holds a numbered requirement heading. Open questions is left out, since its entries are numbered headings too.
