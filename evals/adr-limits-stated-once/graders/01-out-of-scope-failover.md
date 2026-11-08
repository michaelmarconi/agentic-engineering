---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: '## Out of scope(?:(?!\n## )[\s\S])*fail'
flags: i
weight: 1
---
Out of scope names the untested failover.
