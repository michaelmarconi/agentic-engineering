---
type: regex
target: last_message
pattern: '\*\*Question 1 of \d+[^\n]*\*\*(?:(?!\n\s*-{3}\s*\n)[\s\S])*\n\s*-{3}\s*\n\s*\*\*Question 2 of \d+'
weight: 1
---
The count runs across both ADRs: the question before the rule is "Question 1 of M" and the one after it is "Question 2 of M", not "Question 1" for each ADR.
