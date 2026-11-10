---
type: regex
target: { source: file, path: docs/adrs/0001-payment-event-handling.md }
pattern: '## Out of scope(?:(?!\n## )[\s\S])*dispute'
flags: i
weight: 1
---
Out of scope still names the card-dispute decision left for later: a true limit stays there.
