---
type: regex
target: { source: file, path: tests/test_wordcount.py }
pattern: 'def test_two_words\(self\):\n        self\.assertEqual\(self\.run_on\("hello  world\\n"\), "2"\)'
flags: m
weight: 1
---
The earlier Count words tests are unchanged.
