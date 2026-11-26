---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}agentic:build-reviewer[\s\S]*"name":"(?:TaskUpdate|TodoWrite)"'
weight: 1
---
The list was updated after the build reviewer started, so the reviews' step was marked as it ended.
