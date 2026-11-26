---
type: regex
target: trace
pattern: '"name":"(?:TaskCreate|TodoWrite)"(?:(?!"name":"Agent")[\s\S])*?subagent_type[^,]{0,8}agentic:spec-reviewer|subagent_type[^,]{0,8}agentic:spec-reviewer(?:(?!"name":"(?:Edit|Write|MultiEdit)")[\s\S])*?"name":"(?:TaskCreate|TodoWrite)"'
weight: 1
---
The review's steps went on the task list when the review started: a task tool was called just before the reviewer started, or right after it and before any correction.
