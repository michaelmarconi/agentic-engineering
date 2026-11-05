---
type: regex
target: { source: file, path: docs/specs/password-reset.spec.md }
pattern: '^## (?!Requirements)[^\n]*\n(?:(?!^## )[\s\S])*^### Requirement:'
flags: m
match: not_contains
weight: 1
---
Every requirement is still under Requirements: no other section holds a "### Requirement:" heading.
