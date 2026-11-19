---
type: regex
target: { source: file, path: docs/brief.md }
pattern: "^## Open questions\\s*\\n\\s*_?None\\._?\\s*($|\\n)"
flags: m
weight: 1
---
The brief's Open questions section says only "None.": the questions are put to the person in the conversation, and none is written into the brief before the person defers it.
