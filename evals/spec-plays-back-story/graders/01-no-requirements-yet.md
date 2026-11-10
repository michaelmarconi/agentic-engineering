---
type: regex
target: trace
pattern: '"file_path":"[^"]*\.spec\.md","(?:content|old_string":"(?:\\.|[^"\\])*","new_string)":"(?:\\.|[^"\\])*### 1\. (?!<)'
match: not_contains
weight: 1
---
No requirement was written before the person agreed the story and scope.
