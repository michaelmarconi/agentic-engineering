---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: "## Question[\\s\\S]*## Decision[\\s\\S]*## Background[\\s\\S]*## Options[\\s\\S]*## Consequences[\\s\\S]*## Out of scope[\\s\\S]*## How we'll check[\\s\\S]*## Open questions[\\s\\S]*## Technical detail"
weight: 1
---
The sections appear in the template's order, plain first and Technical detail last.
