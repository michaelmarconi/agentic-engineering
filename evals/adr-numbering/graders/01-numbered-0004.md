---
type: regex
target: trace
pattern: '"name":"Write","input":\{"file_path":"[^"]*docs/adrs/0004-[a-z0-9]+(-[a-z0-9]+){1,4}\.md"'
weight: 1
---
The new ADR was written as docs/adrs/0004-<subject>.md, with a subject of two to five words.
