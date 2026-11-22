---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: Draft 📝
date: 2026-11-02
---

# Note search

## Story

When someone has hundreds of notes and remembers a few words from one of them, they want to
search for those words, so they can open that note again.

## In scope

- Searching notes by the words in them
- Limiting a search to notes dated within a range

## Out of scope

- Searching other people's notes
- Saving a search to run again later

## Requirements

### 1. Matching notes are shown

WHEN the person searches for one or more words, the system SHALL show every note whose text
contains all of those words.

| Example | One word |
|---|---|
| Given | a note reading `Pay the invoice` and a note reading `Call the bank` |
| When | the person searches for `invoice` |
| Then | `Pay the invoice` is shown |
| And | `Call the bank` is not shown |

| Example | Last day of the range |
|---|---|
| Given | a note dated `2026-01-31` reading `Pay the invoice` |
| And | a date range of `2026-01-01` to `2026-01-31` |
| When | the person searches for `invoice` |
| Then | `Pay the invoice` is shown |

#### How we'll check

Test that stores the notes in each example, runs each search and checks which notes are shown.

### 2. Date range limits the results

WHEN the person searches with a date range, the system SHALL show only notes dated within it,
both ends included.

| Example | First day of the range |
|---|---|
| Given | a note dated `2026-01-01` reading `Pay the invoice` |
| And | a date range of `2026-01-01` to `2026-01-31` |
| When | the person searches for `invoice` |
| Then | `Pay the invoice` is shown |

| Example | Day before the range |
|---|---|
| Given | a note dated `2025-12-31` reading `Pay the invoice` |
| And | a date range of `2026-01-01` to `2026-01-31` |
| When | the person searches for `invoice` |
| Then | no note is shown |

| Example | Last day of the range |
|---|---|
| Given | a note dated `2026-01-31` reading `Pay the invoice` |
| And | a date range of `2026-01-01` to `2026-01-31` |
| When | the person searches for `invoice` |
| Then | `Pay the invoice` is shown |

| Example | Day after the range |
|---|---|
| Given | a note dated `2026-02-01` reading `Pay the invoice` |
| And | a date range of `2026-01-01` to `2026-01-31` |
| When | the person searches for `invoice` |
| Then | no note is shown |

#### How we'll check

Test that stores a note on each date in the examples, searches with the range and checks which
notes are shown.

### 3. Nothing found

IF no note matches a search, THEN the system SHALL show `No notes found`.

| Example | No match |
|---|---|
| Given | a note reading `Call the bank` |
| When | the person searches for `invoice` |
| Then | `No notes found` is shown |

#### How we'll check

Test that searches for a word no stored note contains and checks the message.

### 4. Notes with every word are listed

WHEN the person searches, the system SHALL list each note that includes every word searched for.

| Example | Two words |
|---|---|
| Given | a note reading `Pay the gas bill` and a note reading `Pay the invoice` |
| When | the person searches for `pay bill` |
| Then | `Pay the gas bill` is listed |
| And | `Pay the invoice` is not listed |

#### How we'll check

Test that stores both notes, searches for two words and checks only the note holding both is
listed.

## Constraints

- None.

## Open questions

- None.
