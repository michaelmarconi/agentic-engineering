---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '## Out of scope\s(?:(?!\n## )[\s\S])*payroll'
flags: i
weight: 1
---
Out of scope names payroll.
