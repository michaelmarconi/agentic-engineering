---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: Draft
date: 2026-10-20
---

# Send email through a queue

## Context and Problem Statement

Sign-up, password reset and invoice emails are sent while the web request waits. When the email
provider is slow, pages take up to 20 seconds to load, and when it is down the request fails and
the person sees an error even though their action succeeded.

## Considered Options

- Send through a queue: requests add the email to a queue and a separate worker sends it.
- Send in the request: rejected because a slow or failing provider slows or fails the person's
  request.
- Send in a background thread of the web process: rejected because emails waiting in memory are
  lost when the process restarts.

## Decision Outcome

Chosen option: send through a queue, because the person's request no longer waits on the
provider, and a queued email survives a restart and is retried until it is sent.

### Consequences

- Good: pages that send email load as fast as the rest, and a provider outage delays emails
  instead of failing requests.
- Bad: there is one more service to run and monitor, and an email can now arrive a few
  minutes late while the queue drains.

### Confirmation

Applies to: any code that sends an email.
Checked by: inspection that request-handling code only adds emails to the queue and that only
the worker calls the email provider.

## Open questions

None.
