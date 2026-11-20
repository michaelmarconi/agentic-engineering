---
type: regex
target: trace
pattern: '"name":"(?:Write|Edit)","input":\{(?:"replace_all":(?:true|false),)?"file_path":"[^"]*(?:/AGENTS\.md|/script/[^"]+)"(?:,"old_string":"(?:[^"\\]|\\.)*")?,"(?:new_string|content)":"(?:[^"\\]|\\.)*uv run ruff check|"name":"Bash"[^\n]*?> ?script/[a-z-]+[^\n]*uv run ruff check'
weight: 1
---
The lint command is the one CI runs, recorded in AGENTS.md or in a script under script/ that a
recorded step calls, as the skill does for a step of more than one command.
