---
type: regex
target: { source: file, path: AGENTS.md }
pattern: 'docs/practices/testing\.md[\s\S]*docs/practices/testing\.md'
match: not_contains
weight: 1
---
The core names the topic file once.
