---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}sdlc:spec-reviewer[\s\S]*"new_string":"(?:\\.|[^"\\])*status: Ready to build'
weight: 1
---
The reviewer was started before the status was set to Ready to build.
