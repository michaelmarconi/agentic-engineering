---
type: regex
target: trace
pattern: '(?:"name":"(?:Write|Edit)"[^\n]*?"file_path":"[^"]*/AGENTS\.md"|"name":"(?:Write|Edit)"[^\n]*?"file_path":"[^"]*/script/[^"]+"|"name":"Bash"[^\n]*?> ?script/[a-z-]+)[^\n]*uv run ruff check'
weight: 1
---
The lint command is the one CI runs, recorded in AGENTS.md or in a script under script/ that a
recorded step calls, as the skill does for a step of more than one command.
