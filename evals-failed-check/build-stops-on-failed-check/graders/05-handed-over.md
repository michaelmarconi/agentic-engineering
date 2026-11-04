---
type: regex
target: { source: file, path: .git/pushes.log }
pattern: '^refs/heads/build/word-count$'
flags: m
weight: 1
---
The build branch was still handed over: it was pushed to origin.
