---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: '## Technical detail[\s\S]*(?:appendfsync|noeviction)'
weight: 1
---
Technical detail holds the Redis settings.
