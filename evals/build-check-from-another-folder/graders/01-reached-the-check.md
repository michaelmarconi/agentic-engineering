---
type: regex
target: trace
pattern: '"subagent_type":\s*"agentic:build-correction-checker"|--reviews-passed"'
weight: 1
---
The build got past its reviews: either it started the build correction checker (which the hook used to refuse in this layout) or every review passed and it handed over with --reviews-passed. Whether the plan ends Built also depends on what the reviews find, which this case does not test.
