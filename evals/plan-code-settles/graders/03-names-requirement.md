---
type: regex
target: trace
pattern: '"name":"Write","input":\{"file_path":"[^"]*docs/plans/[^"]*","content":"(?:\\.|[^"\\])*customs-hold-alerts\.spec\.md\)(?:\\.|[^"\\])*\[Release recorded\]\([^)]*#2-release-recorded\)(?:\\.|[^"\\])*adrs/0003-'
weight: 1
---
The plan written lists the customs hold alerts spec with a link to its "Release recorded" requirement beneath it, and ADR 0003 after.
