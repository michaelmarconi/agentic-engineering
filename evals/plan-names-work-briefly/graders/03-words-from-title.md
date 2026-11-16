---
type: regex
target: trace
pattern: '"name":"Write","input":\{"file_path":"[^"]*docs/plans/\d{4}-\d{2}-\d{2}-(?:record|when|the|broker|releases|a|held|shipment)(?:-(?:record|when|the|broker|releases|a|held|shipment)){1,4}\.md"'
weight: 1
---
The plan's file name is made only of words from its title.
