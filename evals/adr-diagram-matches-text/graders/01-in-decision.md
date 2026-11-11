---
type: regex
target: { source: file, path: docs/adrs/0001-customs-status-updates.md }
pattern: '## Decision\s+Chosen:[^#]*?```\s*mermaid[\s\S]*?```\s*## Background'
weight: 1
---
The diagram is a mermaid block in Decision, after the "Chosen:" sentence and before Background.
