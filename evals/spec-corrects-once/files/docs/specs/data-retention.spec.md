---
status: ✅ Built
---

# Data retention

## Problem

Priya, who runs compliance, was asked by an auditor to prove that customer records older than
a year are deleted, and could not, because nothing is ever deleted.

## Goal

Customer records are kept no longer than the law here allows.

## Scope

In:
- Deleting customer records

Out:
- Backups

## Requirements

### Requirement: Delete old customer records

WHEN a customer record has not been changed for 365 days, the system SHALL delete it.

#### Scenario: Just over a year
- GIVEN a customer record last changed 366 days ago
- WHEN the daily clean-up runs
- THEN the record no longer exists

#### Scenario: Just under a year
- GIVEN a customer record last changed 364 days ago
- WHEN the daily clean-up runs
- THEN the record still exists

Verified by: test with a controllable clock that checks records at 364 and 366 days.

## Constraints

- None.

## Open questions

- None.
