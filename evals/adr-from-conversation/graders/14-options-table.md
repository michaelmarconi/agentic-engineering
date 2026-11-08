---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: '## Options\s+\|[^\n]*Option[^\n]*Outcome[^\n]*Why[\s\S]*\|\s*Chosen\s*\|[\s\S]*\|\s*Rejected\s*\|'
weight: 1
---
Options is a table with Option, Outcome and Why columns, marking options Chosen and Rejected.
