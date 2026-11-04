---
type: regex
target: { source: file, path: AGENTS.md }
pattern: '^- [^\n]*(before|when|while)[\s\S]{0,200}?docs/practices/testing\.md|^- [^\n]*docs/practices/testing\.md[^\n]*(before|when|while)'
flags: im
weight: 1
---
One line in the core names the topic file and says when to read it.
