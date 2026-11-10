---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}agentic:spec-reviewer[\s\S]*Result: PASS[\s\S]*"(new_string|content)":"(?:\\.|[^"\\])*status: (?:\\.|[^"\\]){0,16}Accepted'
weight: 1
---
A passing review report arrived before the status was set to Accepted.
