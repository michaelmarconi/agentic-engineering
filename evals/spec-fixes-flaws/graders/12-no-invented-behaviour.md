---
type: llm
focus: { source: file, path: docs/specs/invoice-export.spec.md }
weight: 1
---
No requirement or scenario adds behaviour beyond what the original spec described. The original
described only this behaviour: a finance user exports one invoice as a PDF; the PDF includes the
invoice number, the customer's name and the total, and looks professional; a paid invoice's PDF
shows a "PAID" stamp with the payment date; the export is fast. Concrete example values in
scenarios, a scenario for an unpaid invoice that only checks a PDF is produced, Scope lists, and
how a requirement is verified are not new behaviour. New behaviour, such as who may not export,
error handling or limits, must appear only as open questions.
