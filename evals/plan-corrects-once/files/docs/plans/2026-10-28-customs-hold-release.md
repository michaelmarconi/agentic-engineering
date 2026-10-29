---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
---

# Customs hold release

## Specs

- [Customs hold alerts](../specs/customs-hold-alerts.spec.md)
  - Requirement: Release recorded

## ADRs

- [0003 Keep each shipment's status as a history of events](../adrs/0003-shipment-status-history.md)

## Decisions

- Show "cleared since <time>" on the container's page in place of "held since": the support team
  asked to see when a hold ended when customers call.

## Plan

Releases reported by the customs broker are ignored today, so released containers stay in the
list of held containers. A release becomes a "cleared" status event, recorded through
`record_status()` in `src/shipments.py`, the way `src/broker/updates.py` already records holds,
as the status history ADR requires. The list in `src/holds/list.py` already reads each
container's latest event, so a cleared container drops out of it with no change there. Telling
anyone about a release is left for later, as [the brief](../brief.md) says. Each release
is also kept in a new Redis cache, so the page can read it quickly.

1. Write the failing test from the spec's scenario: hold at 2027-02-12 09:12, release at
   2027-02-13 14:30.
2. Turn the broker's "released" message into a "cleared" event in `src/broker/updates.py`.
3. Show "cleared since <time>" in `summary()` in `src/page.py`.

```python
if message["type"] == "released":
    record_status(message["container"], "cleared", at)
```

## Open questions

- None.
