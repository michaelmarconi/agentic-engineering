---
type: regex
target: trace
pattern: '"name":"Write"[^\n]*?"file_path":"[^"]*/script/[^"]+"[^\n]*python3 -m build[^\n]*git push --tags'
weight: 1
---
A script under script/ runs the build, the tag and the push, in that order.
