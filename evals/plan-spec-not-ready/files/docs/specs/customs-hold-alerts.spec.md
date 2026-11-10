---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: 📝 Draft
---

# Customs hold alerts

## Story

When customs holds a container at the port, the logistics coordinator at a furniture
importer wants to see the held container as soon as the customs broker reports the hold,
and see it leave the list once the broker reports its release, so they can act before the
customer calls to ask where their sofa is.

## In scope

- Holds and releases reported by the customs broker.
- Emailing the coordinator when a container is released.

## Out of scope

- Telling customers about holds.

## Requirements

### 1. Hold recorded

When the customs broker reports a hold on a container, the system SHALL add the container to the
list of held containers, showing the time of the hold.

| Example | Hold reported |
|---|---|
| Given | container MSCU1234567 is not held |
| When | the broker reports a hold at 2027-02-12 09:12 |
| Then | the list of held containers shows MSCU1234567, held since 2027-02-12 09:12 |

#### How we'll check

Test, feeding a recorded broker hold message to the update handler.

### 2. Release recorded

When the customs broker reports the release of a held container, the system SHALL remove the
container from the list of held containers and show the time of the release on its page.

| Example | Release reported |
|---|---|
| Given | container MSCU1234567 is held since 2027-02-12 09:12 |
| When | the broker reports its release at 2027-02-13 14:30 |
| Then | the list of held containers no longer shows MSCU1234567 |
| And | its page shows cleared since 2027-02-13 14:30 |

#### How we'll check

Test, feeding a recorded broker release message to the update handler.

### 3. Coordinator emailed on release

When the customs broker reports the release of a held container, the system SHALL email the
logistics coordinator within 5 minutes, naming the container and the time of the release.

| Example | Release emailed |
|---|---|
| Given | container MSCU1234567 is held since 2027-02-12 09:12 |
| When | the broker reports its release at 2027-02-13 14:30 |
| Then | by 2027-02-13 14:35 the coordinator has an email saying MSCU1234567 was released at 2027-02-13 14:30 |

#### How we'll check

Test, with a stand-in email server that records the messages it receives.

## Constraints

- None.

## Open questions

- Should a release that arrives before its hold is recorded be kept? Proposed: yes, and matched
  to the hold when it arrives.
