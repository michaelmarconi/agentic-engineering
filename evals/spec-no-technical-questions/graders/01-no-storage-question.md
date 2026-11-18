---
type: regex
target: { source: file, path: docs/specs/page-views.spec.md }
pattern: "postgres|redis|database|data store"
flags: i
match: not_contains
weight: 1
---
The spec, Open questions included, never names the storage choice nor asks about it.
