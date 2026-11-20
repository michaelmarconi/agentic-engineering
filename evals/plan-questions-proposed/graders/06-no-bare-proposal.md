---
type: regex
target: { source: file, path: .eval/document.md }
pattern: '^## Open questions\s*\n(?:(?!^## )[\s\S])*?^### \d+\.[^\n]*\n(?:(?!#{2,3} )(?!> \*\*Why:\*\*)[^\n]*\n)*(?:#{2,3} |(?!#{2,3} )(?!> \*\*Why:\*\*)[^\n]*(?![\s\S]))'
flags: m
match: not_contains
weight: 1
---
No entry under Open questions lacks its quoted "**Why:**" line, so the reason sits apart from the proposal.
