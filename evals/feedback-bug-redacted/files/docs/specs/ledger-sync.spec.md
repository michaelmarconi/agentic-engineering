---
type: Spec
status: 📝 Draft
---

# Ledger sync

## Problem

Priya, an operations analyst at Northwind Bank, reconciles the overnight ledger by hand every
morning. When the LedgerSync service misses a batch she only finds out when a customer calls.

## Goal

Every posted transaction reaches the general ledger by 06:00, and missed batches are reported.

## Scope

In: nightly sync from the core banking platform to the general ledger.
Out: intraday sync; reconciliation of card transactions.

## Requirements

### Requirement: Nightly reconciliation

The system SHALL publish every posted transaction to the Kafka topic `nw.ledger.events` on
https://kafka.internal.northwind-bank.example before 06:00.

#### Scenario: All transactions posted

- Given 12,000 transactions posted on 3 March
- When the nightly sync runs
- Then all 12,000 appear in the general ledger by 06:00 on 4 March

Verified by: test, a sync of a recorded day's transactions against a stand-in ledger.

## Constraints

None.

## Open questions

None.
