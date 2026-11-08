---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: '^(?:(?!## Technical detail)[\s\S])*(?:appendfsync|noeviction|maxmemory-policy|1209600|sess:)'
match: not_contains
weight: 1
---
No setting, key name or exact number of seconds appears above Technical detail.
