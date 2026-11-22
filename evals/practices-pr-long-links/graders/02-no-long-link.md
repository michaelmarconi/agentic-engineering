---
type: regex
target: { source: file, path: .pr-body.md }
pattern: 'https?://[^\s<>()\[\]{}"''`\\]{143,}'
match: not_contains
weight: 1
---
No link address in any recorded description is longer than 150 characters.
