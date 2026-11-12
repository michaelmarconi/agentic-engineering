---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-09-01
---

# Keep customer records in a hosted database in the United States

## Question

Where are customers' names, phone numbers and email addresses kept?

## Decision

Chosen: a hosted database run by a provider in its United States region (us-east-1), because it
was the cheapest option on offer.

## Background

Bookings need each customer's name, phone number and email address.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| A file on the shop's computer | Rejected | It is lost if the computer breaks |

## Consequences

- Good: no server to look after.
- Bad: none known.

## Out of scope

None.

## How we'll check

Applies to: the code that stores customer records.

1. Inspection: customer records are written only to the hosted database.

## Open questions

None.

## Technical detail

None.
