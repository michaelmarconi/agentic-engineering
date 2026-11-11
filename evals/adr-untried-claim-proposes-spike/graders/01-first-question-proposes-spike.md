---
type: regex
target: { source: file, path: docs/adrs/0001-payment-event-handling.md }
pattern: '## Open questions\s+### 1\.\s(?:(?!\n### |\n## )[\s\S])*?(?:spike|experiment)'
flags: i
weight: 1
---
The first open question proposes a spike.
