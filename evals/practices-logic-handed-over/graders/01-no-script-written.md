---
type: regex
target: trace
pattern: '(?:"name":"Write"[^\n]*?"file_path":"[^"]*/scripts?/[^"]*"|"command":"[^"]*scripts?/)[^\n]*docker push'
match: not_contains
weight: 1
---
No deploy script is written, since the step needs logic. A script for the read-only check is allowed.
