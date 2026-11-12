---
type: regex
target: trace
pattern: '"skill":\s*"(?:agentic:)?build"'
match: not_contains
weight: 1
---
Claude does not start the build in this session.
