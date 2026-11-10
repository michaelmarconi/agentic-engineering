---
type: regex
target: { source: file, path: .git/pushes.log }
pattern: '^refs/heads/wc/'
flags: m
weight: 1
---
The build pushed a branch named as the practices in AGENTS.md say, starting `wc/`, although CLAUDE.md does not import AGENTS.md.
