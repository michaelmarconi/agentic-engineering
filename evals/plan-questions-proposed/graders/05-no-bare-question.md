---
type: regex
target: { source: file, path: docs/plans/2026-11-10-coordinator-release-email.md }
pattern: '^## Open questions\s*\n(?:(?!^## )[\s\S])*?^### \d+\.[^\n]*\n(?:(?!#{2,3} )(?!> \*\*Proposed:\*\*)[^\n]*\n)*(?:#{2,3} |(?![\s\S]))'
flags: m
match: not_contains
weight: 1
---
No entry under Open questions lacks its quoted "**Proposed:**" line.
