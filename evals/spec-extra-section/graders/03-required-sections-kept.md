---
type: regex
target: { source: file, path: docs/specs/password-reset.spec.md }
pattern: '^## Story\s*$[\s\S]*^## In scope\s*$[\s\S]*^## Out of scope\s*$[\s\S]*^## Requirements\s*$[\s\S]*^## Constraints\s*$[\s\S]*^## Open questions\s*$'
flags: m
weight: 1
---
The six required sections are all still there, in their order.
