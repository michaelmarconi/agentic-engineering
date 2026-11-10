---
type: Spec
status: 👍 Accepted
---

# Data retention

## Story

When an auditor asks Priya, who runs compliance, to prove that customer records older than a
year are deleted, Priya wants records kept no longer than the law here allows, so they can show
the auditor that they are.

## In scope

- Deleting customer records

## Out of scope

- Backups

## Requirements

### 1. Delete old customer records

WHEN a customer record has not been changed for 365 days, the system SHALL delete it.

| Example | Just over a year |
|---|---|
| Given | a customer record last changed 366 days ago |
| When | the daily clean-up runs |
| Then | the record no longer exists |

| Example | Just under a year |
|---|---|
| Given | a customer record last changed 364 days ago |
| When | the daily clean-up runs |
| Then | the record still exists |

#### How we'll check

Test with a controllable clock that checks records at 364 and 366 days.

## Constraints

- None.

## Open questions

- None.
