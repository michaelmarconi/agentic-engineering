---
type: regex
target: trace
pattern: '"file_path":"[^"]*/src/[^"]*\.py"'
match: not_contains
weight: 1
---
No code was written under src/.
