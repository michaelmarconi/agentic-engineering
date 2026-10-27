---
type: regex
target: trace
pattern: '"file_path":"[^"]*docs/adrs/000[123]-\S*?","(old_string|content)"'
match: not_contains
weight: 1
---
None of the existing ADRs 0001 to 0003 was written or edited.
