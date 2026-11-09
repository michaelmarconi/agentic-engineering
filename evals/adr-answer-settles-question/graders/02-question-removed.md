---
type: regex
target: { source: file, path: docs/adrs/0003-how-email-is-sent.md }
pattern: "^## Open questions\\s*\\n\\s*(?:[-*] +)?None\\.?[ \\t]*\\n(?:\\s*\\n)*(?:## Technical detail|\\[\\^|$(?![\\s\\S]*\\S))"
flags: m
weight: 1
---
The Open questions section now says only "None." (Technical detail or footnotes may follow it).
