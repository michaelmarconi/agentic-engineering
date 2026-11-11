---
type: regex
target: { source: file, path: AGENTS.md }
pattern: 'architecture decision record|\[\^[^\]]+\]'
flags: i
match: not_contains
weight: 1
---
The core spells out no lifecycle term and adds no footnote defining one.
