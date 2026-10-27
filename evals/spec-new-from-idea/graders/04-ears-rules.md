---
type: regex
target: { source: file, path: docs/specs/password-reset.spec.md }
pattern: "### Requirement:[^\\n]*\\n(?:(?!SHALL)[^#])*#### Scenario"
match: not_contains
weight: 1
---
Every requirement has a rule using SHALL between its "### Requirement:" heading and its first scenario.
