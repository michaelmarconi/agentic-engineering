---
type: regex
target: { source: file, path: docs/specs/add-task.spec.md }
pattern: '(\]\(\s*<?[^)]*|^\s*\[[^\]]+\]:\s*<?\S*|(href|src)\s*=\s*["''][^"'']*)(architecture\.md|src/|tasks\.ts)'
flags: im
match: not_contains
weight: 1
---
The spec links neither to the architecture page nor to the code.
