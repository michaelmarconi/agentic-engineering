---
type: regex
target: trace
pattern: '"file_path":"[^"]*login-sessions\.spec\.md","(old_string|content)"'
match: not_contains
weight: 1
---
The spec was neither written nor edited.
