---
type: regex
target: trace
pattern: '"name":"(Write|Edit)"[^\n]*"file_path":\s*"[^"]*(AGENTS\.md|docs/practices/[^"]*)"[^\n]*\.github/pull_request_template\.md'
weight: 1
---
The practices written in this run hold a rule naming .github/pull_request_template.md.
