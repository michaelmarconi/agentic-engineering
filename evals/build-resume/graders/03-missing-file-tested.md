---
type: regex
target: { source: file, path: tests/test_wordcount.py }
pattern: 'No such file: '
flags: m
weight: 1
---
A test checks the No such file message.
