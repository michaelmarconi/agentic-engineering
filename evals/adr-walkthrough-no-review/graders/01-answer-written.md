---
type: regex
target: { source: file, path: docs/adrs/0003-how-email-is-sent.md }
pattern: "(in memory|lost)[\\s\\S]*^## Open questions"
flags: m
weight: 1
---
The answer, that emails held in memory are lost when the web process restarts, is written into the ADR before Open questions.
