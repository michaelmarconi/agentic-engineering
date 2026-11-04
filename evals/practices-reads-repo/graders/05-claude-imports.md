---
type: regex
target: { source: file, path: CLAUDE.md }
pattern: '^@AGENTS\.md\s*$'
flags: m
weight: 1
---
CLAUDE.md imports AGENTS.md.
