---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Plan
status: 📝 Draft
---

# Customs hold release

## Specs

- [Customs hold alerts](../specs/customs-hold-alerts.spec.md)[^hold]
  - [Release recorded](../specs/customs-hold-alerts.spec.md#2-release-recorded)

## ADRs

| ADR | Decision |
| --- | --- |
| [0003](../adrs/0003-shipment-status-history.md) | Keep each shipment's status as a history of events |

## Decisions

- Message types are looked up in a dict from type to status, not an if/else chain: two types fit on two lines.
- The release is a "cleared" event in the existing status history, with no new table: ADR 0003 already keeps status as events.
- The test's release message `tests/messages/release.json` is copied from `hold.json` with the type changed: it keeps the two messages alike.
- The cleared line is added to `summary()` rather than a new function: the page has one summary and nothing else calls it.
- The broker connection times out after 30 seconds: the broker can take up to 25 seconds to
  answer, and a shorter wait cut off slow answers.

## Plan

A customs hold stops a shipping container from leaving the port, and a release ends it. The customs
broker[^broker] reports each hold and release to the system, but releases are ignored today, so
released containers stay in the list of held containers. A release becomes a "cleared" status
event, "cleared" being the status of a container whose hold has ended, recorded through
`record_status()` in `src/shipments.py`, the way `src/broker/updates.py` already records holds, as
ADR 0003 requires. The list in `src/holds/list.py` already shows only containers whose latest event
is "held", so a cleared container leaves it with no change there. Release messages come slower
than holds, and the connection's 10-second timeout in `src/broker/connection.py` already drops some. Emailing the logistics
coordinator on a release is the spec's next requirement, left for a later plan.

1. Write the failing test from the spec's scenario: hold at 2027-02-12 09:12, release at
   2027-02-13 14:30.
2. Turn the broker's "released" message into a "cleared" event in `src/broker/updates.py`.
3. Show "cleared since <time>" in `summary()` in `src/page.py`.
4. Raise the timeout in `connect()` in `src/broker/connection.py` to 30 seconds.

## Open questions

- None.

[^hold]: An order from the customs authority that a container stay where it is until its goods
    are inspected or its paperwork is approved.
[^broker]: A licensed agent who deals with the customs authority for the company bringing the
    goods into the country.
