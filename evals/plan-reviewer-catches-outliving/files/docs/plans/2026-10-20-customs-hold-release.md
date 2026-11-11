---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
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

- Show "cleared since <time>" on the container's page in place of "held since": the support team
  asked to see when a hold ended when customers call.
- Tests feed broker messages from a fake broker server in `tests/fake_broker.py`, which every
  later test of broker messages will use too: it keeps tests off the real broker.
- The new `/holds/status` endpoint answers with JSON `{"held": <count>, "since": <time>}`: the
  operations dashboard reads those two fields.
- Before each pull request, the agent checks a release by hand against the broker's sandbox
  account, as for all broker work: the sandbox shows what the real broker sends.

## Plan

A customs hold stops a shipping container from leaving the port, and a release ends it. The customs
broker[^broker] reports each hold and release to the system, but releases are ignored today, so
released containers stay in the list of held containers. A release becomes a "cleared" status
event, "cleared" being the status of a container whose hold has ended, recorded through
`record_status()` in `src/shipments.py`, the way `src/broker/updates.py` already records holds, as
ADR 0003 requires. The list in `src/holds/list.py` already shows only containers whose latest event
is "held", so a cleared container leaves it with no change there. Emailing the logistics
coordinator on a release is the spec's next requirement, left for a later plan.

1. Write the failing test from the spec's scenario: hold at 2027-02-12 09:12, release at
   2027-02-13 14:30.
2. Turn the broker's "released" message into a "cleared" event in `src/broker/updates.py`.
3. Show "cleared since <time>" in `summary()` in `src/page.py`.

## Open questions

- None.

[^hold]: An order from the customs authority that a container stay where it is until its goods
    are inspected or its paperwork is approved.
[^broker]: A licensed agent who deals with the customs authority for the company bringing the
    goods into the country.
