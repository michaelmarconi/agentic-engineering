---
type: regex
target: { source: file, path: tests/test_wordcount.py }
pattern: 'assertEqual\(wordcount\.count\(''hello  world\\n''\), 2\)'
flags: m
weight: 1
---
The existing Two words test now expects 2, the spec's value, for the same input.
