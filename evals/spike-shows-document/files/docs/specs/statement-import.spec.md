---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: 📝 Draft
---

# Statement import

## Problem

Each month the accounts clerk retypes the bank's statement into the ledger, line by line.

## Goal

The clerk uploads the statement file the bank sends, and every transaction in it appears in the
ledger.

## Scope

In:
- The monthly statement file from the bank, as the bank sends it.

Out:
- Statements from any other bank.

## Requirements

### Requirement: Import a statement

When the accounts clerk uploads the bank's monthly statement file, the system SHALL add each
transaction in it to the ledger, with its date, payee and amount.

#### Scenario: Statement imported
- GIVEN the ledger holds no transactions for October 2026
- WHEN the clerk uploads the October 2026 statement, holding 12 transactions
- THEN the ledger holds those 12 transactions, each with its date, payee and amount

Verified by: test, importing the sample statement `samples/statement.csv`.

## Constraints

- None.

## Open questions

- Can the system read the statement file as the bank sends it, without anyone converting it
  first? A real statement, with the account number removed, is in `samples/statement.csv`.
