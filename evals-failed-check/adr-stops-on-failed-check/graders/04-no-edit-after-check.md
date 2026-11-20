---
type: regex
target: trace
pattern: 'subagent_type[^,]{0,8}agentic:correction-checker[\s\S]*"name":"(?:Edit|Write|MultiEdit)","input":\{(?:"replace_all":(?:true|false),)?"file_path":"[^"]*docs/adrs/[^"]*\.md"(?!,"old_string":"(?:## Open questions|> \*\*(?:Proposed|Why):\*\*)(?:(?!\\n## )(?:[^"\\]|\\.))*")'
match: not_contains
weight: 1
---
Nothing was changed in the document after the check failed, beyond deferring questions into Open questions when the person said not to ask.
