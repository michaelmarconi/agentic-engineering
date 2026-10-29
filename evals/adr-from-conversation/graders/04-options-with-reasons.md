---
type: llm
focus: { source: file, path: docs/adrs/0001-session-data-storage.md }
weight: 1
---
Considered Options lists Postgres and signed cookies as options not chosen. The ADR gives a reason against each: for cookies, a session cannot be ended from the server; for Postgres, an extra query on every request.
