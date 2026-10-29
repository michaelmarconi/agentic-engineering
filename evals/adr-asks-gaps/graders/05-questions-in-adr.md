---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: "^## Open questions\\s*\\n\\s*[-*] +(?!None\\.?\\s*$)\\S"
flags: m
weight: 1
---
The ADR's Open questions section holds at least one question, so what is missing is written in the ADR, not only asked in chat.
