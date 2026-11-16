---
type: regex
target: trace
pattern: '"name":"(?:Write|Edit|MultiEdit)"[^\n]*?"file_path":"[^"]*(?:AGENTS\.md|docs/practices/)[^\n]*npm run (?!build[\s`"\\])[\w:.-]+'
weight: 1
---
The practices record a one-line npm run command for setting up.
