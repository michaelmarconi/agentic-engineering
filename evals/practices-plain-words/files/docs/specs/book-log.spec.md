---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: 👍 Accepted
date: 2026-11-02
---

# Book log

## Story

When the reader finishes a book, they want to add it to their log, so they can later list every
book they have read, in the order they read them.

## In scope

- What the requirements below say.

## Out of scope

- Anything else.

## Requirements

### 1. Books listed in order

When the reader lists the log, the system SHALL show every book added, oldest first.

| Example | Two books |
|---|---|
| Given | "Middlemarch" added, then "Beloved" |
| When | the reader lists the log |
| Then | "Middlemarch" is shown before "Beloved" |

#### How we'll check

Test.

## Constraints

- None.

## Open questions

- None.
