---
type: regex
target: { source: file, path: docs/specs/word-count.spec.md }
pattern: '^\| Example \| [^\n]*\|\s*$\n^\|-{3}\|-{3}\|'
flags: m
weight: 1
---
Examples are tables.
