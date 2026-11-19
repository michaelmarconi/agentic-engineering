---
type: regex
target: { source: file, path: docs/specs/password-reset.spec.md }
pattern: "^## Open questions\\s*\\n\\s*[-*]?\\s*[*_]{0,2}None\\.[*_]{0,2}\\s*($|\\n)"
flags: m
weight: 1
---
The spec's Open questions section says only "None.": the questions are put to the person in the conversation, and none is written into the spec before the person defers it.
