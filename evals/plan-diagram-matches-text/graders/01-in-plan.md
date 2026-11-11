---
type: regex
target: { source: file, path: docs/plans/2026-10-20-customs-hold-release.md }
pattern: '## Plan\s*\n\n[^`\n](?:(?!\n## )[\s\S])*?```\s*mermaid(?:(?!\n## )[\s\S])*?```'
weight: 1
---
The diagram is a mermaid block in the Plan section, after its opening paragraph.
