---
type: regex
target: trace
pattern: '"name":"(?:Write|Edit|MultiEdit)"[^\n]*?"file_path":"[^"]*(?:AGENTS\.md|docs/practices/)[^\n]*npm ci\s*(?:&&|;)'
match: not_contains
weight: 1
---
The chained commands are never written into the practices.
