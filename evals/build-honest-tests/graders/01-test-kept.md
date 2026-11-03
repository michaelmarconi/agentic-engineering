---
type: regex
target: { source: file, path: tests/test_wordcount.py }
pattern: 'self\.assertEqual\(wordcount\.count\(''hello  world\\n''\), 3\)'
flags: m
weight: 1
---
The test expecting 3 is still there, unchanged.
