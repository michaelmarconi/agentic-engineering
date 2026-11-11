---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: 2026-10-20
---

# Send email through a queue

## Question

How should the web app send its emails, so a slow or failing email provider never slows down a request?

## Decision

Chosen: send email through a queue, which requests add to and a separate worker sends from. The
person's request no longer waits on the provider, and a queued email survives a restart and is
retried until it is sent.

## Background

Sign-up, password reset and invoice emails are sent while the web request waits. When the email
provider is slow, pages take up to 20 seconds to load. When it is down, the request fails and
the person sees an error even though their action succeeded.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Send through a queue | Chosen | Requests never wait on the provider, and queued emails survive restarts |
| Send in the request | Rejected | A slow or failing provider slows or fails the person's request |
| Send in a background thread of the web process | Rejected | |

## Consequences

- Good: pages that send email load as fast as the rest.
- Good: a provider outage delays emails instead of failing requests.
- Bad: there is one more service to run and monitor.
- Bad: an email can arrive a few minutes late while the queue drains.

## Out of scope

None.

## How we'll check

Applies to: any code that sends an email.

1. Inspection shows request-handling code only adds emails to the queue.
2. Inspection shows only the worker calls the email provider.

## Open questions

### 1. Why a background thread was rejected

The ADR does not say why sending in a background thread of the web process was rejected.

> **Proposed:** Tell me what ruled it out.
>
> **Why:** Only you know the reason.

### 2. How often a failed email is retried

The ADR does not say how many times a failed email is retried before it is given up.

> **Proposed:** Five times.
>
> **Why:** Five tries ride out a short outage without retrying forever.

### 3. Which queue service runs the queue

The ADR chooses a queue but not the service that runs it.

> **Proposed:** The Redis the app already uses.
>
> **Why:** It adds no new service to run.

## Technical detail

None.
