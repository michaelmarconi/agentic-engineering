---
type: regex
target: { source: file, path: docs/specs/invoice-export.spec.md }
pattern: "^## Out of scope\\s*\\n(?:\\s*\\n)*- (?!Not (?:known|decided)|None\\b)|^### \\d+\\. [^\\n]*(?:out of scope|will not do|won't do|leave out|left out)"
flags: mi
weight: 1
---
Out of scope names at least one thing that is not covered, or, since the person asked for what
needs their decision to be left as open questions, an open question asks what is out rather than
the spec guessing.
