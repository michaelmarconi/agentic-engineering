---
type: regex
target: { source: file, path: docs/specs/password-reset.spec.md }
pattern: '^status: [^\x00-\x7F]'
flags: m
match: not_contains
weight: 1
---
The status is no longer written with its emoji in front, as the plugin's earlier versions wrote it.
