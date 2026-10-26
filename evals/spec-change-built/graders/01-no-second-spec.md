---
type: regex
target: trace
pattern: "docs/specs/(?!password-reset\\.spec\\.md)[\\w./-]*\\.spec\\.md"
match: not_contains
weight: 1
---
No spec other than password-reset.spec.md is named anywhere in the run, so no second spec was written.
