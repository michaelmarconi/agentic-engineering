---
type: regex
target: { source: file, path: docs/adrs/0002-catalogue-copy-refresh.md }
pattern: "\\bADR[ -]?0*1\\b(?![^\\[\\]\\n]*\\]\\()"
match: not_contains
weight: 1
---
No mention of ADR 0001 is left as a bare number, outside a link.
