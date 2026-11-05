---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '^## Problem\s*$[\s\S]*^## Who it.s for\s*$[\s\S]*^## Goals\s*$[\s\S]*^## Out of scope\s*$[\s\S]*^## Constraints\s*$[\s\S]*^## Open questions\s*$'
flags: m
weight: 1
---
The six required sections are all still there, in their order.
