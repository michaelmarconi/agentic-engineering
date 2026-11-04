---
type: regex
target: trace
pattern: '"name":"(Write|Edit|MultiEdit)"[^\n]*test_[^\n]*default|"name":"(Write|Edit|MultiEdit)"[^\n]*default[^\n]*test_'
flags: i
weight: 1
---
The naming practice that was written says it is a default.
