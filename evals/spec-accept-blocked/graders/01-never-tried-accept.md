---
type: regex
target: trace
pattern: '"(new_string|content)":"(?:(?:\\.|[^"\\])*status: *(?:\\.|[^"\\]){0,16})?(?:Accepted|Ready)'
match: not_contains
weight: 1
---
No Write or Edit tried to set the spec to `👍 Accepted` or any kind of Ready, so the skill held back rather than leaving it to the hook.
