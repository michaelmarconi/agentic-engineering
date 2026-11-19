---
type: regex
target: last_message
pattern: '\A(?![\s\S]*\*\*Question \d+ of \d+[^\n]*\*\*[\s\S]*\*\*Question \d+ of \d+)[\s\S]*\*\*Question \d+ of \d+[^\n]*\*\*'
weight: 1
---
The reply asks exactly one question, with one bold "Question N of M" line, and leaves the others for later replies.
