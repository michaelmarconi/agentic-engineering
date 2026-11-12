---
type: regex
target: last_message
pattern: '^ {0,3}>[ \t]*\n {0,3}> ?\*\*Why:\*\* *\S'
flags: m
weight: 1
---
The reason sits in the block quote, on a line starting "**Why:**", with a line holding only ">" before it, so it shows on a line of its own.
