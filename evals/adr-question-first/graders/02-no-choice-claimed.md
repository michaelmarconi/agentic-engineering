---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: '\|\s*\**Chosen\**\s*\||^\**Chosen\**:'
flags: m
match: not_contains
weight: 1
---
No option is marked Chosen and the Decision claims no choice.
