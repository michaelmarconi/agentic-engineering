---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: '^type: ADR\s*$'
flags: m
weight: 1
---
The superseded ADR, which had no type line, now has `type: ADR` in its frontmatter.
