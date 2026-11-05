---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-09-01
---

# Export with Python's csv module

## Context and Problem Statement

The accountant exports a year of invoices at once, about 10,000 of them, and it must be quick.

## Considered Options

- The other way: rejected, it was worse.

## Decision Outcome

Chosen option: Python's csv module, because it quotes fields correctly and is fast enough for a year of invoices.

### Consequences

- Good: it is simpler.
- Bad: none known.

### Confirmation

Applies to: the export code.
Checked by: test: running `python3 tests/bench_export.py` prints the time taken to export 10,000 invoices, which must be under 1.0 seconds.

## Open questions

- None.
