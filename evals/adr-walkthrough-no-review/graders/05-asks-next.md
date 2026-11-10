---
type: regex
target: last_message
pattern: "(retr|queue service|which queue|redis)[^\\n]*\\?"
flags: i
weight: 1
---
The reply goes on to one of the two remaining open questions: how many times a failed email is retried, or which queue service runs the queue.
