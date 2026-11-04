---
type: regex
target: trace
pattern: '"name":"(Write|Edit|MultiEdit)"[^\n]*(?:\\n|":")(?:[^\\]|\\")*test_(?:[^\\]|\\")*\(default\)'
flags: i
weight: 1
---
The line of the naming practice that was written ends by saying it is a default.
