---
type: regex
target: { source: file, path: docs/adrs/0001-payment-event-handling.md }
pattern: '## Out of scope(?:(?!\n## )[\s\S])*\border'
flags: i
match: not_contains
weight: 1
---
Out of scope does not list the untried claim about the order of events as a limit.
