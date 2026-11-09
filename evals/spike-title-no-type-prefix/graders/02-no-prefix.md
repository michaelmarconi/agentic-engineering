---
type: regex
target: trace
pattern: '"file_path":"[^"]*docs/spikes/[^"]+\.md","content":"(?:\\.|[^"\\])*\\n# *(?:\*\*)?spike(?: record)?\s*[:—–-]'
flags: i
match: not_contains
weight: 1
---
The record's title does not start with "Spike:" or "Spike record:".
