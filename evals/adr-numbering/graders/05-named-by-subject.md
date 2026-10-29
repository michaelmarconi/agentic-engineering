---
type: regex
target: trace
pattern: '"file_path":"[^"]*docs/adrs/0004-(?:(?:send|use|queue|move|adopt|choose|put|run|switch)-|[^"]*-(?:through|via|with|in|on|to)-a-)'
match: not_contains
weight: 1
---
The new ADR's file name does not state the decision the way its title does, as in 0004-send-email-through-a-queue.md or 0004-use-a-queue-for-email.md.
