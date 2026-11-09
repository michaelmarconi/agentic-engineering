---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '^---\n(?:#[^\n]*\n)*type: Brief\n'
weight: 1
---
The brief's frontmatter names it as a brief, with type: Brief.
