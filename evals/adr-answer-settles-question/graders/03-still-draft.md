---
type: regex
target: { source: file, path: docs/adrs/0003-how-email-is-sent.md }
pattern: "^status: Draft\\s*$"
flags: m
weight: 1
---
The person answered a question but did not accept the ADR, so it stays Draft.
