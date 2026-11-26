---
type: regex
target: trace
pattern: '"name":"(?:TaskCreate|TodoWrite)"(?:(?!"name":"(?!TaskCreate|TodoWrite)")[\s\S])*?Check that the corrections broke nothing'
weight: 1
---
The list holds the build's fixed steps as the script gives them, the correction check among them.
