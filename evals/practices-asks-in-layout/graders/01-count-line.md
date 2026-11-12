---
type: regex
target: last_message
pattern: '\*\*(?:Question|Topic|Decision) 1 of \d+\b[^\n]*\*\*'
weight: 1
---
The question opens with a bold line naming it and its place in the count, such as "**Question 1 of 2: ...**".
