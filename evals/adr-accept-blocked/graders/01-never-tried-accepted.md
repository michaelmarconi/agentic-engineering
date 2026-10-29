---
type: regex
target: trace
pattern: '"(new_string|content)":"(?:(?:\\.|[^"\\])*status: *)?Accepted'
match: not_contains
weight: 1
---
No Write or Edit tried to set the ADR to Accepted, so the skill held back rather than leaving it to the hook.
