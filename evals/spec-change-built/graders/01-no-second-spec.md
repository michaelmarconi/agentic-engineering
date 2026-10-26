---
type: regex
target: trace
pattern: '"name":"Write","input":\{"file_path":"[^"]*(?<!/docs/specs/password-reset\.spec\.md)"'
match: not_contains
weight: 1
---
No Write went to any file but the existing spec, so no second spec was created anywhere.
