---
type: llm
focus: { source: file, path: docs/adrs/0001-session-data-storage.md }
weight: 1
---
Options lists Postgres and signed cookies as rejected options. The ADR gives a reason against each: for cookies, a session cannot be ended from the server; for Postgres, an extra query on every request.
