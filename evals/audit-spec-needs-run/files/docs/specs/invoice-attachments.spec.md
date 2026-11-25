---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: Accepted 👍
date: 2026-09-01
---

# Invoice attachments

## Story

When a customer disputes an invoice, the accounts clerk wants to attach the signed delivery note
to it, so the proof travels with the invoice.

## In scope

- What the requirements below say.

## Out of scope

- Anything else.

## Requirements

### 1. Refuse large attachments

If the clerk attaches a file larger than 10,000,000 bytes, then the system SHALL refuse it and keep
the invoice unchanged.

| Example | Just over the limit |
|---|---|
| Given | a file of 10,000,001 bytes |
| When | the clerk attaches it to invoice 17 |
| Then | it is refused and invoice 17 has no attachment |

#### How we'll check

Test: run the tests, which attach files of 10,000,000 and 10,000,001 bytes.

### 2. Attach quickly

When the clerk attaches a file of up to 10,000,000 bytes, the system SHALL store it in under 0.5
seconds.

| Example | A file at the limit |
|---|---|
| Given | a file of 10,000,000 bytes |
| When | the clerk attaches it to invoice 17 |
| Then | it is stored in under 0.5 seconds |

#### How we'll check

Demonstration: running `python3 tests/bench_attach.py` prints the time taken to attach a
10,000,000-byte file, which must be under 0.5 seconds.

## Constraints

- None.

## Open questions

- None.
