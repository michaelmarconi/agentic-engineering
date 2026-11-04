---
type: regex
target: { source: file, path: AGENTS.md }
pattern: '`[^`\n]*(<[A-Za-z_-]+>|--watch|\bptw\b|\.\.\.)[^`\n]*`'
match: not_contains
weight: 1
---
No command holds a placeholder or waits in watch mode.
