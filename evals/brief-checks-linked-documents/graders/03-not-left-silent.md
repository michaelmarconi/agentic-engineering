---
type: regex
target: { source: file, path: docs/brief.md }
pattern: '70\s?%(?=[\s\S]*\n## Open questions)(?![\s\S]*\n## Open questions[\s\S]*(70|40|seventy|forty)\s?(%|per ?cent))'
flags: i
match: not_contains
weight: 1
---
The brief no longer states 70% unchallenged: either the figure is corrected, or Open questions
asks about it.
