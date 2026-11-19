---
type: regex
target: trace
pattern: '(?:"name":"(?:Write|Edit)"[^\n]*?"file_path":"[^"]*docs/practices/ci[^"]*"|"name":"(?:Write|Edit)"[^\n]*?"file_path":"[^"]*/script/[^"]+"|"name":"Bash"[^\n]*?> ?script/[a-z-]+)[^\n]*(?:uv run ruff check[^\n]*uv run pytest|uv run pytest[^\n]*uv run ruff check)'
weight: 1
---
The pipeline's lint and test commands are written down to run locally, in the topic file or in a
script under script/.
