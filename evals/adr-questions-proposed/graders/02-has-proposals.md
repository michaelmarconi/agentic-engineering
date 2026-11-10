---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: '^## Open questions\s*\n(?:(?!^## )[\s\S])*?^\s*[-*] (?!<)[^\n]*(?:\n(?![-*] |## )[^\n]*)*Proposed:'
flags: m
weight: 1
---
Open questions holds at least one proposed answer.
