---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: "^## Open questions\\s*\\n\\s*[-*]?\\s*[*_]{0,2}None\\.[*_]{0,2}\\s*($|\\n)"
flags: m
weight: 1
---
The ADR's Open questions section says only "None.": the questions are put to the person in the conversation, and none is written into the ADR before the person defers it.
