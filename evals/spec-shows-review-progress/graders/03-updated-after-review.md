---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}agentic:spec-reviewer[\s\S]*"name":"(?:TaskUpdate|TodoWrite)"'
weight: 1
---
The list was updated after the reviewer started, so the review's step was marked as it ended.
