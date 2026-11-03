---
type: regex
target: { source: file, path: .git/commits.log }
pattern: '^=== [^\n]*\n(?:(?!=== |src/)[^\n]*\n)*tests/test_wordcount\.py\n(?:(?!=== |src/)[^\n]*\n)*=== [\s\S]*?^src/wordcount\.py$'
flags: m
weight: 1
---
A commit holding tests and no code under src/ came before the first commit holding src/wordcount.py.
