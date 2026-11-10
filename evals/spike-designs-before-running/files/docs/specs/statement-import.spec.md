---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: 📝 Draft
---

# Statement import

## Story

When the bank's monthly statement arrives, the accounts clerk wants to upload the statement
file the bank sends and have every transaction in it appear in the ledger, so they can stop
retyping the statement line by line.

## In scope

- The monthly statement file from the bank, as the bank sends it.

## Out of scope

- Statements from any other bank.

## Requirements

### 1. Import a statement

When the accounts clerk uploads the bank's monthly statement file, the system SHALL add each
transaction in it to the ledger, with its date, payee and amount.

| Example | Statement imported |
|---|---|
| Given | the ledger holds no transactions for October 2026 |
| When | the clerk uploads the October 2026 statement, holding 12 transactions |
| Then | the ledger holds those 12 transactions, each with its date, payee and amount |

#### How we'll check

Test, importing the sample statement `samples/statement.csv`.

## Constraints

- None.

## Open questions

- Can the system read the statement file as the bank sends it, without anyone converting it
  first? A real statement, with the account number removed, is in `samples/statement.csv`.
  Proposed: find out by trying the importer on that sample.
