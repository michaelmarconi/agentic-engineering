---
type: regex
target: { source: file, path: docs/specs/page-views.spec.md }
pattern: "(?i)postgres|redis|database|data store"
match: not_contains
weight: 1
---
The spec, Open questions included, never names the storage choice nor asks about it.
