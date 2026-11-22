---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: Accepted 👍
date: 2026-11-20
---

# Pull the owner's mail into the local copy

As the owner, I want my mail copied to this computer, so that I can search it offline.

## Requirements

### 1. Messages that cannot be searched by meaning are reported in the pull status

When a pull finishes, the pull status shall give the number of messages that cannot be searched by
meaning.

### 2. Searching by meaning is tried again for every such message after each later pull

When a pull finishes, the gateway shall try again to make each message searchable by meaning.

## Out of scope

- None.

## Open questions

- None.
