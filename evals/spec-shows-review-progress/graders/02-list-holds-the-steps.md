---
type: regex
target: trace
pattern: '"name":"(?:TaskCreate|TodoWrite)"(?:(?!"name":"(?!TaskCreate|TodoWrite)")[\s\S])*?[Cc]heck (?:that )?the corrections'
weight: 1
---
The list holds the review sequence's fixed steps, the check of the corrections among them, rather than steps the agent made up.
