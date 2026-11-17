---
type: regex
target: { source: file, path: docs/practices/releasing.md }
pattern: 'python3 -m build'
match: not_contains
weight: 1
---
The release commands themselves are not written into the practice.
