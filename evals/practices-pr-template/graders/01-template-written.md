---
type: regex
target: { source: file, path: .github/pull_request_template.md }
pattern: '^## Summary\s*$[\s\S]*^## Built from\s*$'
flags: m
weight: 1
---
The project gains the default pull request template, opening with a Summary and then what the work was built from.
