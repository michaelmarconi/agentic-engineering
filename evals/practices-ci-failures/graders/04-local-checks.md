---
type: regex
target: trace
pattern: '"name":"(?:Write|Edit)"[^\n]*"file_path":\s*"[^"]*docs/practices/ci[^\n]*(?:uv run ruff check[^\n]*uv run pytest|uv run pytest[^\n]*uv run ruff check|`script/[a-z-]+`)'
weight: 1
---
The topic file gives how to run the pipeline's checks locally: the commands themselves, or the
script under script/ that runs them, as the skill does for a step of more than one command.
