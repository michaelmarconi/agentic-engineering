---
type: regex
target: { source: file, path: docs/adrs/0003-how-email-is-sent.md }
pattern: "the person sees an error even though their action succeeded\\.[\\s\\S]*an email can arrive a few minutes late while the queue drains\\.[\\s\\S]*2\\. Inspection shows only the worker calls the email provider\\.\\n\\n## Open questions\\n\\nNone\\.\\n\\n## Technical detail\\n\\nNone\\.\\n?$"
weight: 1
---
The ADR's text is unchanged apart from its status.
