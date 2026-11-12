---
type: regex
target: last_message
pattern: '(run|type|send|use)\W{0,4}/clear'
flags: i
weight: 1
---
The reply tells the person to run /clear, not only mentions it.
