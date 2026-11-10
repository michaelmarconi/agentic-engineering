---
type: Spec
status: 📝 Draft
---

# Invoice export

## Story

When finance staff need an invoice, finance staff want a PDF export button on the invoices page, so they
can get invoices out of the system quickly.

## In scope

- Exporting one invoice as a PDF

## Out of scope

## Requirements

### 1. Export an invoice

The system SHALL let a finance user export an invoice as a PDF. The PDF SHALL include the
invoice number, the customer's name and the total, and SHALL look professional.

| Example | Export |
|---|---|
| Given | an invoice |
| When | a finance user exports it |
| Then | a PDF of the invoice is produced |

#### How we'll check

Test.

### 2. Paid stamp

When an invoice has been paid, the PDF shows a "PAID" stamp with the payment date.

| Example | Paid invoice |
|---|---|
| Given | invoice INV-1042 for £120.00, paid in full on 3 March 2026 |
| When | a finance user exports it |
| Then | the PDF shows "PAID 3 March 2026" |

#### How we'll check

Test that pays INV-1042 through the live card payment gateway, exports it and
checks the stamp.

## Open questions

- None.

## Constraints

- The export must be fast.
