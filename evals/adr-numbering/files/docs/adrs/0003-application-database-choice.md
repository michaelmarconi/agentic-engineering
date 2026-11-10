---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-10-20
---

# Use Postgres for application data

## Question

Which database holds the application's accounts, invoices and settings?

## Decision

Chosen: use Postgres for application data, because the team knows it.

## Background

The application needs one database for accounts, invoices and settings.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Postgres | Chosen | The team knows it |
| MySQL | Rejected | The team knows Postgres |

## Consequences

- Good: no learning curve.
- Bad: one server to run.

## Out of scope

None.

## How we'll check

Applies to: any code that stores application data.

1. Inspection shows application data is stored only in Postgres.

## Open questions

None.

## Technical detail

None.
