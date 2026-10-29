---
type: regex
target: { source: file, path: docs/adrs/0001-settlement-file-import.md }
pattern: "pile-?up"
flags: i
match: not_contains
weight: 1
---
The team's nickname "the 2 a.m. pile-up" is replaced by what it means, since a newcomer would have to guess it.
