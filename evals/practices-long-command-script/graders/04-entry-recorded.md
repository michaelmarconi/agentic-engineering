---
type: regex
target: { source: file, path: docs/practices/running.md }
pattern: '`(?:npm run|pnpm(?: run)?|yarn) [\w:.-]+`'
weight: 1
---
The running practice records the package.json entry's one-line command.
