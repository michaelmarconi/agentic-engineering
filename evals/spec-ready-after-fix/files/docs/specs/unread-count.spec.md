---
status: Draft
---

# Unread count

## Problem

Lena gets about forty notifications a day and cannot tell how many she has not opened yet, so
each morning she clicks through all of them to find the new ones and often misses one that came
in overnight.

## Goal

People can see at a glance how many of their notifications they have not opened yet.

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

Verified by: test.

### Requirement: Opening a notification

WHEN a person clicks a notification in the list that they have not opened before, the system
SHALL count it as opened from then on.

#### Scenario: First open
- GIVEN the bell icon shows 3
- WHEN Lena clicks one of her unopened notifications in the list
- THEN the bell icon shows 2 without the page being reloaded
- AND it still shows 2 after the page is reloaded

#### Scenario: Last unopened
- GIVEN the bell icon shows 1
- WHEN Lena clicks her last unopened notification in the list
- THEN the bell icon shows no number without the page being reloaded

#### Scenario: Opening one already opened
- GIVEN the bell icon shows 2
- WHEN Lena clicks a notification she opened yesterday
- THEN the bell icon still shows 2

Verified by: test that starts with 3 unopened notifications, clicks one (checks 2), clicks an
already opened one (checks still 2), then clicks the other two (checks 1, then no number),
checking the bell after each click both without reloading and after a reload.

## Constraints

- None.

## Open questions

- None.
