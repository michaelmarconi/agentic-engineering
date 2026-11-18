---
type: regex
target: last_message
pattern: '\*\*Question 2 of \d+\b[^\n]*\*\*'
weight: 1
---
The next question counts the one already settled, so it is "**Question 2 of N: ...**", not question 1 again.
