---
type: regex
target: last_message
pattern: '^ {0,3}> ?\*\*Why:\*\* *\S'
flags: m
weight: 1
---
The reason sits in the block quote, on a line starting "**Why:**".
