---
type: regex
target: { source: file, path: .git/HEAD }
pattern: '^ref: refs/heads/build/word-count\s*$'
flags: m
weight: 1
---
The build ran on a branch named build/word-count.
