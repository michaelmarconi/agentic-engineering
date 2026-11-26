---
type: regex
target: { source: file, path: .git/commits.log }
pattern: '^src/wordcount\.py$'
flags: m
weight: 1
---
The build went ahead without stopping: a pushed commit holds src/wordcount.py.
