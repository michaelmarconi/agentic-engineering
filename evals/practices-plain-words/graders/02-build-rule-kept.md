---
type: regex
target: { source: file, path: AGENTS.md }
pattern: 'Never open a pull request from an `/agentic:build` run until its plan is `✅ Built`\.'
weight: 1
---
The rule naming `/agentic:build` is in the core word for word.
