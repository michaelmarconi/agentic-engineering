---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Plan
status: Built ✅
date: 2026-11-21
---

# Report and retry messages that cannot be searched by meaning

## Specs

- [Pull the owner's mail into the local copy](../specs/mail-pull.spec.md)
  - [Messages that cannot be searched by meaning are reported in the pull status](../specs/mail-pull.spec.md#1-messages-that-cannot-be-searched-by-meaning-are-reported-in-the-pull-status)
  - [Searching by meaning is tried again for every such message after each later pull](../specs/mail-pull.spec.md#2-searching-by-meaning-is-tried-again-for-every-such-message-after-each-later-pull)

## ADRs

None.

## Decisions

- The count is kept in memory and set by each pull.

## Plan

Add the count to the pull status and retry failed messages after each pull.

## Open questions

None.
