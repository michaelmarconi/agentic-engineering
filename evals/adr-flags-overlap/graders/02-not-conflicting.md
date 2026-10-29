---
type: regex
target: trace
pattern: '"file_path":"[^"]*0003-session-storage-service\.md","content":"(?![^"]*supersedes: (\\")?0002)'
match: not_contains
weight: 1
---
If the new ADR was written, it names 0002 in a supersedes line, so the two do not stand as conflicting decisions.
