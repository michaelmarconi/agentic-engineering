---
type: regex
target: { source: file, path: docs/specs/password-reset.spec.md }
pattern: "SHALL\\b.*\\bSHALL\\b"
match: not_contains
weight: 1
---
No rule uses SHALL more than once, so each requirement states one rule.
