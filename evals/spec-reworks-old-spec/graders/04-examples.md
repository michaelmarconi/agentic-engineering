---
type: regex
target: { source: file, path: docs/specs/word-count.spec.md }
pattern: '^\| Example \| [^\n]*\|\s*$\n^\|---\|---\|'
flags: m
weight: 1
---
Examples are tables.
