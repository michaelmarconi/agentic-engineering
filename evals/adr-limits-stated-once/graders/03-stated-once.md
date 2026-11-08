---
type: llm
focus: { source: file, path: docs/adrs/0001-session-data-storage.md }
weight: 1
---
Out of scope states both limits, that failover was not load-tested and that backing Redis up is a separate decision, and no other section states either again; Consequences in particular holds neither, though another section may refer to Out of scope. Consequences still names the bad result that everyone logs in again if Redis loses its data.
