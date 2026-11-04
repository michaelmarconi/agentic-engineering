---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
---

# Word count

## Problem

Asha writes articles for a magazine whose editor rejects any article over 800 words. She drafts
in a plain text editor that shows no word count, so before sending each article she pastes it
into a website to count the words, and twice this year she sent one that was over the limit.

## Goal

A writer can count the words in a text file from the command line.

## Scope

In:
- Counting the words in one plain text file named on the command line

Out:
- Counting characters or lines
- Reading from standard input

## Requirements

### Requirement: Count words

WHEN a person runs `wordcount <file>` on a file that exists, the system SHALL print the number of
words in it, where a word is a run of characters that are not whitespace.

#### Scenario: Two words
- GIVEN a file holding `hello  world` followed by a newline
- WHEN the person runs `wordcount` on it
- THEN the system prints `2`

#### Scenario: Empty file
- GIVEN an empty file
- WHEN the person runs `wordcount` on it
- THEN the system prints `0`

Verified by: unit tests for both scenarios, run on temporary files.

### Requirement: Missing file

IF the file named does not exist, THEN the system SHALL print `No such file: <name>` and exit with
status 1.

#### Scenario: File not there
- GIVEN no file named `draft.txt`
- WHEN the person runs `wordcount draft.txt`
- THEN the system prints `No such file: draft.txt` and exits with status 1

Verified by: a unit test that runs the command on a name with no file behind it.

## Constraints

- None.

## Open questions

- None.
