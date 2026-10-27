---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '\]\(|docs/|\.spec\.md|decisions/|0001|postgres'
flags: i
match: not_contains
weight: 1
---
The brief has no Markdown link, no path to the spec or the ADR, and no mention of PostgreSQL.
