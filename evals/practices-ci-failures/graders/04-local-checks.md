---
type: regex
target: trace
pattern: '"name":"(?:Write|Edit)","input":\{(?:"replace_all":(?:true|false),)?"file_path":"[^"]*docs/practices/ci[^"]*"(?:,"old_string":"(?:[^"\\]|\\.)*")?,"(?:new_string|content)":"(?:[^"\\]|\\.)*(?:uv run ruff check(?:[^"\\]|\\.)*uv run pytest|uv run pytest(?:[^"\\]|\\.)*uv run ruff check|`script/[a-z-]+`)'
weight: 1
---
The topic file gives how to run the pipeline's checks locally: the commands themselves, or the
script under script/ that runs them, as the skill does for a step of more than one command.
