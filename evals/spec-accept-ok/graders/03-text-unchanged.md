---
type: regex
target: trace
pattern: '("name":"Write","input":\{"file_path":"[^"]*unread-count\.spec\.md)|("file_path":"[^"]*unread-count\.spec\.md","old_string":"(?!status: ))'
match: not_contains
weight: 1
---
The only edit to the spec was the status line, so Accepted was set on the text the person handed over.
