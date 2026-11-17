---
type: regex
target: trace
pattern: '"name":"(Write|Edit)"[^\n]*"file_path":\s*"[^"]*(AGENTS\.md|docs/practices/[a-z0-9-]+\.md)"[^\n]*structlog'
weight: 1
---
The recorded practice names structlog, the library the repository already uses.
