---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-10-20
---

# Use Postgres for application data

## Context and Problem Statement

The application needs one database for accounts, invoices and settings.

## Considered Options

- Postgres
- MySQL: rejected because the team knows Postgres.

## Decision Outcome

Chosen option: Postgres, because the team knows it.

### Consequences

- Good: no learning curve.
- Bad: one server to run.

### Confirmation

Applies to: any code that stores application data.
Checked by: inspection that application data is stored only in Postgres.

## Open questions

None.
