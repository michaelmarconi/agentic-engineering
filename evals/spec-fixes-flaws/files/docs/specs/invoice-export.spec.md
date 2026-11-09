---
type: Spec
status: 📝 Draft
---

# Invoice export

## Problem

Finance staff need a PDF export button on the invoices page.

## Goal

Finance can get invoices out of the system quickly.

## Scope

In:
- Exporting one invoice as a PDF

## Requirements

### Requirement: Export an invoice

The system SHALL let a finance user export an invoice as a PDF. The PDF SHALL include the
invoice number, the customer's name and the total, and SHALL look professional.

#### Scenario: Export
- GIVEN an invoice
- WHEN a finance user exports it
- THEN a PDF of the invoice is produced

Verified by: test.

### Requirement: Paid stamp

When an invoice has been paid, the PDF shows a "PAID" stamp with the payment date.

#### Scenario: Paid invoice
- GIVEN invoice INV-1042 for £120.00, paid in full on 3 March 2026
- WHEN a finance user exports it
- THEN the PDF shows "PAID 3 March 2026"

Verified by: test that pays INV-1042 through the live card payment gateway, exports it and
checks the stamp.

## Open questions

- None.

## Constraints

- The export must be fast.
