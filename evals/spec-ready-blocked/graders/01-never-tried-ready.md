---
type: regex
target: trace
pattern: '"(new_string|content)":"(?:\\.|[^"\\])*status: Ready to build'
match: not_contains
weight: 1
---
No Write or Edit tried to set the spec to Ready to build, so the skill held back rather than leaving it to the hook.
