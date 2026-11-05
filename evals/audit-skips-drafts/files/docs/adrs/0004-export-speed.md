---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-09-01
---

# Export with the standard csv module, writing as it goes

## Context and Problem Statement

The accountant exports a year of invoices at once, about 10,000 of them.

## Considered Options

- The other way: rejected, it was worse.

## Decision Outcome

Chosen option: the csv module, writing each row as it is made, because it needs no memory for the whole file.

### Consequences

- Good: it is simpler.
- Bad: none known.

### Confirmation

Applies to: the export code.
Checked by: test: running `python3 tests/bench_export.py` prints the time taken to export 10,000 invoices, which must be under 1.0 seconds.

## Open questions

- None.
