---
type: regex
target: trace
pattern: '(?:"name":"Write"[^\n]*?"file_path":"[^"]*/script/[^"]+"|"name":"Bash"[^\n]*?"command":"[^"]*?>\s*(?:\./)?script/[^\s"]+)[^\n]*doveadm[^\n]*Test Folder'
weight: 1
---
A script under script/ runs the copy with the test folder written in.
