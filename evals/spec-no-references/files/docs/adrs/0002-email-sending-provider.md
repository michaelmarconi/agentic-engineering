---
type: ADR
status: 👍 Accepted
---

# Send email through Postmark

## Question

Which provider sends the product's account emails?

## Decision

Chosen: send account emails through Postmark, because its delivery rates for account emails are
the best of the providers we tried.

## Background

The product sends account emails, such as reset links, and needs a provider that delivers them
reliably.

## Open questions

None.
