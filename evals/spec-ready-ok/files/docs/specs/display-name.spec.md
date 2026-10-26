---
status: Draft
---

# Display name

## Problem

Tomás signed up with the display name "tomas_1987", which every teammate now sees next to his
comments. He wants it to read "Tomas Ruiz", but the only way to change it today is to email
support, who take two working days to reply.

## Goal

People can change their own display name themselves, and teammates see the new name next to
their comments from the next time they load a page.

## Scope

In:
- Changing your own display name from your account settings
- The name shown next to your comments

Out:
- Changing someone else's display name
- Changing the email address used to sign in
- Anywhere else a name might appear, such as emails already sent

## Requirements

### Requirement: Change display name

WHEN a signed-in person saves a display name that, after spaces at either end are removed, is
1 to 50 characters long, the system SHALL store it without those spaces and show it next to
their comments on every page loaded afterwards.

#### Scenario: Spaces at either end
- GIVEN Tomás is signed in with the display name "tomas_1987"
- WHEN he saves " Tomas Ruiz "
- THEN his comments show "Tomas Ruiz" on the next page load

#### Scenario: Longest allowed name
- GIVEN Tomás is signed in
- WHEN he saves a name of exactly 50 letters
- THEN all 50 letters are shown next to his comments on the next page load

Verified by: test that saves " Tomas Ruiz " and a 50-letter name, then loads a page with one of
his comments and checks the name shown.

### Requirement: Reject names outside the limits

IF a signed-in person saves a display name that, after spaces at either end are removed, is
empty or longer than 50 characters, THEN the system SHALL keep the current name and show the
message "Display name must be 1 to 50 characters."

#### Scenario: Only spaces
- GIVEN Tomás is signed in with the display name "tomas_1987"
- WHEN he saves "   "
- THEN his display name stays "tomas_1987"
- AND he sees "Display name must be 1 to 50 characters."

#### Scenario: One letter too long
- GIVEN Tomás is signed in with the display name "tomas_1987"
- WHEN he saves a name of 51 letters
- THEN his display name stays "tomas_1987"
- AND he sees "Display name must be 1 to 50 characters."

Verified by: test that saves an empty name, "   " and a 51-letter name, and checks each time
that the name is unchanged and the message is shown.

## Constraints

- None.

## Open questions

- None.
