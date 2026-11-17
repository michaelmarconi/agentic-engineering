---
type: regex
target: trace
pattern: '"name":"(Write|Edit)"[^\n]*"file_path":\s*"[^"]*(AGENTS\.md|docs/practices/[a-z0-9-]+\.md)"[^\n]*var/log/stockroom\.jsonl'
weight: 1
---
The recorded practice says where the logs end up, var/log/stockroom.jsonl, read from the repository.
