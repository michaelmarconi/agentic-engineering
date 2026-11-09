---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
date: 2026-10-27
---

# Refresh the catalogue copy with a nightly full download

## Question

How should each web server's local copy of the catalogue be kept up to date?

## Decision

Chosen: refresh the copy with a nightly full download of the supplier's catalogue, replacing the
old file in one step. The supplier offers a full export, and the catalogue changes only once a
day.

## Background

ADR 0001 serves product pages from a local SQLite copy of the catalogue on each web server. That
copy is filled by hand today, so it falls behind whenever someone forgets.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Nightly full download | Chosen | Simple, and the supplier changes the catalogue once a day |
| Hourly download of changes only | Rejected | The supplier offers no list of changes |
| Fill the copy on each page miss | Rejected | Pages would still wait on the service when the copy lacks a product |

## Consequences

- Good: every copy is at most a day behind the supplier.
- Bad: a product added during the day appears only the next morning.

## Out of scope

None.

## How we'll check

Applies to: any code that fills or replaces the local catalogue copy.

1. Demonstration: after the nightly run, the local copy holds every product in the supplier's export.

## Open questions

None.

## Technical detail

None.
