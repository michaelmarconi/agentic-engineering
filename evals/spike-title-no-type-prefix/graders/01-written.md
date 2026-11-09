---
type: regex
target: trace
pattern: '"file_path":"[^"]*docs/spikes/[^"]+\.md","content":"(?:\\.|[^"\\])*type: Spike\\n'
weight: 1
---
A spike record was written in docs/spikes/ with `type: Spike` in its frontmatter.
