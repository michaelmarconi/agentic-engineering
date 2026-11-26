---
type: regex
target: trace
pattern: '"name":"(?:TaskCreate|TodoWrite)"(?:(?!"name":"(?:Edit|Write|MultiEdit)")[\s\S])*?subagent_type[^,]{0,8}agentic:spec-reviewer|subagent_type[^,]{0,8}agentic:spec-reviewer(?:(?!"name":"(?:Edit|Write|MultiEdit)")[\s\S])*?"name":"(?:TaskCreate|TodoWrite)"'
weight: 1
---
The review's steps went on the task list when the review started: a task tool was called after the spec was last written and before the reviewer started, or after the reviewer started and before any correction.
