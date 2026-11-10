---
type: Spec
status: 📝 Draft
---

# Ledger sync

## Story

When Priya, an operations analyst at Northwind Bank, reconciles the overnight ledger each
morning, Priya wants every posted transaction to have reached the general ledger by 06:00, and
any missed batch reported, so they can deal with it before a customer calls.

## In scope

- Nightly sync from the core banking platform to the general ledger.

## Out of scope

- Intraday sync.
- Reconciliation of card transactions.

## Requirements

### 1. Nightly reconciliation

The system SHALL publish every posted transaction to the Kafka topic `nw.ledger.events` on
https://kafka.internal.northwind-bank.example before 06:00.

| Example | All transactions posted |
|---|---|
| Given | 12,000 transactions posted on 3 March |
| When | the nightly sync runs |
| Then | all 12,000 appear in the general ledger by 06:00 on 4 March |

#### How we'll check

Test, a sync of a recorded day's transactions against a stand-in ledger.

## Constraints

None.

## Open questions

None.
