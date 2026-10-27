---
type: llm
focus: { source: file, path: docs/specs/invoice-export.spec.md }
weight: 1
---
Every Verified by line names a method and what it checks (no bare "test."). The original wish that the PDF "look professional" is not verified by an automated test: it is either gone from the requirements (for example, turned into an open question) or verified by inspection or demonstration. Automated tests that check text in the PDF, such as invoice numbers, totals or the words of a stamp, are fine and are not judgements of looks.
