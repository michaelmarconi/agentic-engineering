---
type: regex
target: trace
pattern: '"name":"(?:Write|Edit|MultiEdit)"[^\n]*?"file_path":"[^"]*(?:AGENTS\.md|docs/practices/)[^\n]*docker exec mail-test doveadm'
match: not_contains
weight: 1
---
The long docker exec line is never written into the practices.
