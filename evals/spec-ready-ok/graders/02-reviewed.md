---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}sdlc:spec-reviewer[\s\S]*Result: PASS[\s\S]*"(new_string|content)":"(?:\\.|[^"\\])*status: Ready to build'
weight: 1
---
A passing review report arrived before the status was set to Ready to build.
