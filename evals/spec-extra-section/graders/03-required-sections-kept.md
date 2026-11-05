---
type: regex
target: { source: file, path: docs/specs/password-reset.spec.md }
pattern: '^## Problem\s*$[\s\S]*^## Goal\s*$[\s\S]*^## Scope\s*$[\s\S]*^## Requirements\s*$[\s\S]*^## Constraints\s*$[\s\S]*^## Open questions\s*$'
flags: m
weight: 1
---
The six required sections are all still there, in their order.
