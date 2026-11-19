---
type: regex
target: last_message
pattern: '\*\*Question \d+ of \d+[^\n]*\*\*[\s\S]*?\*\*Proposed:\*\*[\s\S]*?\*\*Why:\*\*[^\n]*\n(?:(?!\*\*Question)[^\n]*\n)*?\s*---\s*\n\s*\*\*Question \d+ of \d+[^\n]*\*\*[\s\S]*?\*\*Proposed:\*\*'
weight: 1
---
The first question is laid out whole, from its bold line through its Proposed and Why block, before a line holding only `---`, and the second question's bold line and Proposed block come after that rule.
