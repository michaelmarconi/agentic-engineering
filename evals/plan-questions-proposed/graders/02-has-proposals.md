---
type: regex
target: { source: file, path: docs/plans/2026-11-10-coordinator-release-email.md }
pattern: '^## Open questions\s*\n(?:(?!^## )[\s\S])*?^\s*[-*] (?!<)[^\n]*(?:\n(?![-*] |## )[^\n]*)*Proposed:'
flags: m
weight: 1
---
Open questions holds at least one proposed answer.
