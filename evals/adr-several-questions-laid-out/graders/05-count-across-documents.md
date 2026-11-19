---
type: regex
target: last_message
pattern: '\*\*Question (\d+) of \d+[\s\S]*\*\*Question (?!\1 of)\d+ of \d+'
weight: 1
---
The count runs across both ADRs: the two questions carry different first numbers, such as "Question 1 of 4" and "Question 2 of 4", not "Question 1" for each ADR.
