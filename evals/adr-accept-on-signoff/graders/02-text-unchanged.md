---
type: regex
target: trace
pattern: '("name":"Write","input":\{"file_path":"[^"]*0003-send-email-through-a-queue\.md)|("file_path":"[^"]*0003-send-email-through-a-queue\.md","old_string":"(?!status: ))'
match: not_contains
weight: 1
---
The only edit to the ADR was its status line.
