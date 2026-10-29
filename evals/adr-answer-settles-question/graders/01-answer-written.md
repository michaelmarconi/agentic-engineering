---
type: regex
target: { source: file, path: docs/adrs/0003-how-email-is-sent.md }
pattern: "background thread[^\\n]*(?:\\n[^\\n#-][^\\n]*)*(?:lost|restart)[\\s\\S]*^## Open questions"
flags: m
weight: 1
---
The reason the background thread was rejected, that queued emails are lost on a restart, is written beside that option, before Open questions.
