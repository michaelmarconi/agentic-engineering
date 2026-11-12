---
type: regex
target: { source: file, path: docs/plans/2026-11-10-coordinator-release-email.md }
pattern: '^## Open questions\s*\n(?:(?!^## )[\s\S])*?^### 1\. \S[^\n]*\n(?:(?!^## )[\s\S])*?^> \*\*Proposed:\*\* *\S(?:(?!^## )[\s\S])*?^>[ \t]*\n> \*\*Why:\*\* *\S'
flags: m
weight: 1
---
Open questions holds at least one entry in the layout: a numbered heading, then a block quote holding a "**Proposed:**" line and, after a line holding only ">", a "**Why:**" line.
