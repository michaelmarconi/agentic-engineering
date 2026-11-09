---
type: llm
focus: { source: file, path: docs/adrs/0001-session-data-storage.md }
weight: 1
---
The Decision section's first sentence opens "Chosen:" and names the option in full, such as keeping login sessions in Redis, so that it makes sense with the rest of the ADR hidden. A bare option name, such as "Chosen: Redis." with nothing saying what it is chosen for, fails.
