---
type: regex
target: { source: file, path: docs/adrs/0002-catalogue-copy-refresh.md }
pattern: "\\[[^\\]]*\\b0*1\\b[^\\]]*\\]\\((\\./)?0001-example-store\\.md(#[^)]*)?\\)"
weight: 1
---
The ADR names ADR 0001 as a link to its file, 0001-example-store.md, which exists in docs/adrs/.
