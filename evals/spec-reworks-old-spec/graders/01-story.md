---
type: regex
target: { source: file, path: docs/specs/word-count.spec.md }
pattern: '^## Story\s*$[\s\S]*^## In scope\s*$[\s\S]*^## Out of scope\s*$[\s\S]*^## Requirements\s*$'
flags: m
weight: 1
---
The spec has the new sections in order.
