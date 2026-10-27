---
type: regex
target: { source: file, path: docs/adrs/0003-send-email-through-a-queue.md }
pattern: "the person sees an error even though their action succeeded\\.[\\s\\S]*minutes late while the queue drains\\.[\\s\\S]*Checked by: inspection that request-handling code only adds emails to the queue and that only\\nthe worker calls the email provider\\.\\n?$"
weight: 1
---
The ADR's text is unchanged apart from its status.
