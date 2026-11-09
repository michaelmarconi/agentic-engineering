---
type: llm
focus: { source: file, path: docs/adrs/0001-session-data-storage.md }
weight: 1
---
The Decision opens "Chosen:" and says in plain words that sessions are kept in Redis, without naming any Redis setting, such as appendonly or maxmemory-policy, or the session key format.
