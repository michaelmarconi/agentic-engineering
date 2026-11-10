---
type: regex
target: { source: file, path: docs/specs/password-reset.spec.md }
pattern: "### \\d+\\.[^\\n]*\\n(?:(?!SHALL)[^#|])*\\| Example \\|"
match: not_contains
weight: 1
---
Every requirement has a rule using SHALL between its numbered heading and its first example table.
