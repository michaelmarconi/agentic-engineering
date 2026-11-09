---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-10-20
---

# Serve reads from a local SQLite copy of the catalogue

## Question

Where should the shop's web servers read the product catalogue from?

## Decision

Chosen: serve reads from a local SQLite copy of the catalogue kept on each web server. Pages no
longer wait on the supplier's service, which is slow and often down.

## Background

Every product page calls the supplier's catalogue service. Pages take two seconds at peak, and
fail outright when the service is down, about once a week.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Local SQLite copy on each server | Chosen | Fast reads that keep working while the service is down |
| Call the service on every page | Rejected | Keeps the delay and the weekly failures |
| Shared Redis cache in front of the service | Rejected | Still empty after a restart while the service is down |

## Consequences

- Good: product pages read in milliseconds and survive a supplier outage.
- Bad: each server holds its own copy, which can fall behind the supplier.

## Out of scope

- How the copy is filled from the supplier's service is left to another ADR.

## How we'll check

Applies to: any code that reads product catalogue data.

1. Inspection shows product pages read the catalogue only from the local SQLite file.

## Open questions

None.

## Technical detail

None.
