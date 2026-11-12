---
type: regex
target: last_message
pattern: '^ {0,3}> ?\*\*Proposed:\*\* *\S'
flags: m
weight: 1
---
The proposal sits in a block quote, on a line starting "**Proposed:**".
