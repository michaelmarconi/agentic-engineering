---
status: Draft
---

# Unread count

## Problem

Lena gets about forty notifications a day and cannot tell how many she has not opened yet, so
each morning she clicks through all of them to find the new ones and often misses one that came
in overnight.

## Goal

People can see how many of their notifications they have not opened yet without opening the list.

## Scope

In:
- The number of unopened notifications shown on the bell icon
- Opening one notification by clicking it in the notification list

Out:
- Marking all notifications as opened at once
- Notifications sent by email
- Updating the number in other open tabs or on other devices before their next page load

## Requirements

### Requirement: Show the unread count

WHILE a person has at least one notification they have not opened, the system SHALL show that
number on the bell icon.

#### Scenario: Some unopened
- GIVEN Lena has 40 notifications, 3 of which she has not opened
- WHEN she loads any page
- THEN the bell icon shows 3

Verified by: test that creates 40 notifications, opens 37 and checks the bell shows 3.

### Requirement: Hide the count at zero

WHILE a person has no notification they have not opened, the system SHALL show the bell icon
with no number.

#### Scenario: None unopened
- GIVEN Lena has opened all 40 of her notifications
- WHEN she loads any page
- THEN the bell icon shows no number

Verified by: test that opens all 40 notifications and checks the bell shows no number.

### Requirement: Opening a notification

WHEN a person clicks a notification in the list, the system SHALL count it as opened.

#### Scenario: First open
- GIVEN Lena has 3 notifications she has not opened
- WHEN she clicks one of them in the list and then loads any page
- THEN the bell icon shows 2

#### Scenario: Opening one already opened
- GIVEN Lena has 2 notifications she has not opened
- WHEN she clicks a notification she opened yesterday and then loads any page
- THEN the bell icon still shows 2

Verified by: test that starts with 3 unopened notifications, clicks one and checks the bell
shows 2 after a reload, then clicks an already opened one and checks it still shows 2.

### Requirement: Update the count on click

WHEN a person clicks a notification in the list that they have not opened, the system SHALL
update the number on the bell icon without the page being reloaded.

#### Scenario: One fewer
- GIVEN the bell icon shows 3
- WHEN Lena clicks one of her unopened notifications in the list
- THEN the bell icon shows 2 without the page being reloaded

#### Scenario: Last unopened
- GIVEN the bell icon shows 1
- WHEN Lena clicks her last unopened notification in the list
- THEN the bell icon shows no number without the page being reloaded

Verified by: test that starts with 2 unopened notifications, clicks them one at a time without
reloading, and checks the bell shows 1 and then no number.

## Constraints

- Clicking a notification in the list keeps the person on the same page.

## Open questions

- None.
