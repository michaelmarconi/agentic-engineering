---
type: regex
target: { source: file, path: docs/practices/releasing.md }
pattern: '## Publish[\s\S]*?`(?:\./)?script/[\w.-]+`'
weight: 1
---
The Publish section records the command that runs the script.
