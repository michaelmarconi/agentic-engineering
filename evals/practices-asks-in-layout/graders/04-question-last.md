---
type: regex
target: last_message
pattern: '\?[^\w\n]*(?![\s\S]*\w)'
weight: 1
---
The reply ends with the question itself: nothing but punctuation follows its question mark.
