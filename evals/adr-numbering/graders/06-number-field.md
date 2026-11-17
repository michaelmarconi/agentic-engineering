---
type: regex
target: trace
pattern: 'docs/adrs/0004-[^"]*\.md","content":"---\\n[^"]{0,300}?number: 0004\\n'
weight: 1
---
The new ADR's frontmatter holds `number: 0004`, the four digits its file name starts with.
