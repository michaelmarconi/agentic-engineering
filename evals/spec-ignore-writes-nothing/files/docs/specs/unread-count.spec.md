---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: Draft 📝
date: 2026-11-18
---

# Unread count

## Story

When Sam opens the app after a meeting, Sam wants the bell icon to show how many notifications
they have not opened yet, so they know whether anything needs them.

## In scope

- The number on the bell icon

## Out of scope

- Push notifications to the phone

## Requirements

### 1. Count shown on the bell

When Sam has notifications they have not opened, the app shall show their number on the bell
icon.

| Given | When | Then |
| --- | --- | --- |
| 3 notifications Sam has not opened | Sam opens the app | The bell shows 3 |
| No notifications Sam has not opened | Sam opens the app | The bell shows no number |

**How we'll check:** a test opens the app with 3 unopened notifications and reads the bell.

### 2. Count goes down when one is opened

When Sam opens a notification, the app shall take one off the number on the bell icon.

| Given | When | Then |
| --- | --- | --- |
| The bell shows 3 | Sam opens one notification | The bell shows 2 |

**How we'll check:** a test opens one of 3 notifications and reads the bell.

## Open questions

### 1. Whether a deleted notification still counts as unopened

Sam may delete a notification without opening it.

> **Proposed:** A deleted notification no longer counts.
>
> **Why:** Sam can no longer open it, so counting it would leave a number that never goes away.

### 2. Whether a notification stops counting after some time

Old notifications may no longer matter to Sam.

> **Proposed:** A notification counts until Sam opens or deletes it, however old it is.
>
> **Why:** a count that drops on its own would hide notifications Sam has not seen.
