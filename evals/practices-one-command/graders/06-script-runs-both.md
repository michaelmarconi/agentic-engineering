---
type: regex
target: trace
pattern: '"name":"Write"[^\n]*?"file_path":"[^"]*/script/[^"]+"[^\n]*npm ci[^\n]*npm run build'
weight: 1
---
A script under script/ runs npm ci and then npm run build.
