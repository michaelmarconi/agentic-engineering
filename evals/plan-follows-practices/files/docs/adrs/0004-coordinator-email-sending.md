---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2027-01-20
---

# Send emails with Python's standard smtplib

## Question

How does the system send email to the logistics coordinator about customs holds?

## Decision

Chosen: Python's standard `smtplib`, to the server named by the `SMTP_HOST` setting, because it
needs nothing new installed and the company already runs an email server.

## Background

The system must email the logistics coordinator about customs holds, and has no email code yet.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| A hosted email service's library | Rejected | Adds an outside account and a library to install, for a few emails a day |
| Python's standard `smtplib`, to the server named by the `SMTP_HOST` setting | Chosen | Nothing new to install, and the company already runs an email server |

## Consequences

- Good: no new library or account.
- Bad: retries after a failed send are ours to write.

## Out of scope

None.

## How we'll check

Applies to: any code that sends email.

1. Inspection shows email is sent only through `smtplib`.

## Open questions

- None.

## Technical detail

None.
