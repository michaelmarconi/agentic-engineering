---
type: regex
target: { source: file, path: docs/specs/password-reset.spec.md }
pattern: '^type: Spec\s*$'
flags: m
weight: 1
---
The spec, which had no type line, now has `type: Spec` in its frontmatter.
