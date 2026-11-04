---
type: regex
target: trace
pattern: '"name":"(Write|Edit)"[^\n]*"file_path":\s*"[^"]*docs/practices/ci[^\n]*uv run ruff check[^\n]*uv run pytest|"name":"(Write|Edit)"[^\n]*"file_path":\s*"[^"]*docs/practices/ci[^\n]*uv run pytest[^\n]*uv run ruff check'
weight: 1
---
The topic file gives the commands that run the pipeline's checks locally.
