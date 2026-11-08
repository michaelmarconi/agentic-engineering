---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: '## Out of scope(?:(?!\n## )[\s\S])*back'
flags: i
weight: 1
---
Out of scope names the backup decision left for later.
