---
type: regex
target: { source: file, path: docs/adrs/0001-store-sessions-in-redis.md }
pattern: "src/session"
match: not_contains
weight: 1
---
The Confirmation no longer names file paths.
