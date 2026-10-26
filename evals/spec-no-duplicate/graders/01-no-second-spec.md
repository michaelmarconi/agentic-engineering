---
type: regex
target: trace
pattern: '"file_path":"[^"]*docs/specs/(?!auth/password-reset\.spec\.md")[^"]*\.spec\.md"'
match: not_contains
weight: 1
---
No tool touched a spec file other than the existing auth/password-reset.spec.md.
