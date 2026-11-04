---
type: regex
target: { source: file, path: .git/pushes.log }
pattern: '^refs/heads/build/word-count$'
flags: m
weight: 1
---
The build branch was pushed to origin.
