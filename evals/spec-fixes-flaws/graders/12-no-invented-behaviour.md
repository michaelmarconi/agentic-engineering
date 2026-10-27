---
type: llm
focus: { source: file, path: docs/specs/invoice-export.spec.md }
weight: 1
---
No requirement or scenario adds behaviour beyond what the original spec described. The original
described only this behaviour: a finance user exports one invoice as a PDF; the PDF includes the
invoice number, the customer's name and the total, and looks professional; when an invoice has
been paid, its PDF shows a "PAID" stamp with the payment date (the original's example invoice
was paid in full); the export is fast. A scenario's outcome must follow from its rule: an
outcome the rule does not state or clearly imply is new behaviour, while one it implies, such as
the PDF being of the invoice asked for and no other, is not. Concrete example values, a scenario
for an unpaid invoice that only checks a PDF is produced, Scope lists, and how a requirement is
verified are not new behaviour. New behaviour, which must appear only as open questions,
includes who may not export, error handling, limits, and what happens when a rule's condition
does not hold, such as an unpaid or partly paid invoice showing no stamp or something else.
