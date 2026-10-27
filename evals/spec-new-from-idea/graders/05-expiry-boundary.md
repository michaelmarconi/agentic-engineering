---
type: llm
focus: { source: file, path: docs/specs/password-reset.spec.md }
weight: 1
---
At least one scenario tests the 24-hour expiry at a boundary, with a link just under and/or just over 24 hours old. Times can be given as clock times: a
link issued at 10:00 and used at 10:01 the next day is just over 24 hours old.
