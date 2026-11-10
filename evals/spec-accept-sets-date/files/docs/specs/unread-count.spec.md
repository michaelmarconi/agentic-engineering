---
type: Spec
status: 📝 Draft
date: 2026-10-01
---

# Unopened count

## Story

When forty or so notifications a day come in, Lena wants to see how many have not been
opened yet without opening the list, so they can tell whether any are still unopened,
including ones that came in overnight.

## In scope

- The number of unopened notifications shown on the bell icon
- Opening one notification by clicking it in the notification list

## Out of scope

- Marking all notifications as opened at once
- Notifications sent by email
- Updating the number in other open tabs or on other devices before their next page load

## Requirements

### 1. Show the unopened count

WHILE a person has at least one notification they have not opened, the system SHALL show that
number on the bell icon.

| Example | Some unopened |
|---|---|
| Given | Lena has 40 notifications, 3 of them unopened |
| When | Lena loads any page |
| Then | the bell icon shows 3 |

#### How we'll check

Test that creates 40 notifications, opens 37 and checks the bell shows 3.

### 2. Hide the count at zero

WHILE a person has no notification they have not opened, the system SHALL show the bell icon
with no number.

| Example | None unopened |
|---|---|
| Given | Lena has opened all 40 of Lena's notifications |
| When | Lena loads any page |
| Then | the bell icon shows no number |

#### How we'll check

Test that opens all 40 notifications and checks the bell shows no number.

### 3. Opening a notification

WHEN a person clicks a notification in the list, the system SHALL leave it out of the number on
the bell icon from the next page load on.

| Example | First open |
|---|---|
| Given | Lena has 3 unopened notifications |
| When | Lena clicks one of them in the list and then loads any page |
| Then | the bell icon shows 2 |

| Example | Opening one already opened |
|---|---|
| Given | Lena has 2 unopened notifications |
| When | Lena clicks a notification opened yesterday and then loads any page |
| Then | the bell icon still shows 2 |

#### How we'll check

Test that starts with 3 unopened notifications, clicks one and checks the bell
shows 2 after a reload, then clicks an already opened one and checks it still shows 2.

### 4. Update the count on click

WHEN a person clicks a notification in the list that they have not opened, the system SHALL
update the number on the bell icon without the page being reloaded.

| Example | One fewer |
|---|---|
| Given | the bell icon shows 3 |
| When | Lena clicks one of Lena's unopened notifications in the list |
| Then | the bell icon shows 2 without the page being reloaded |

| Example | Last unopened |
|---|---|
| Given | the bell icon shows 1 |
| When | Lena clicks the last unopened notification in the list |
| Then | the bell icon shows no number without the page being reloaded |

#### How we'll check

Test that starts with 2 unopened notifications, clicks them one at a time without
reloading, and checks the bell shows 1 and then no number.

## Constraints

- None.

## Open questions

- None.
