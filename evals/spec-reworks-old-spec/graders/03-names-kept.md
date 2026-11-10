---
type: regex
target: { source: file, path: docs/specs/word-count.spec.md }
pattern: '^### 1\. Count words\s*$[\s\S]*^### \d+\. Missing file\s*$'
flags: m
weight: 1
---
The requirements keep their names, numbered in their order.
