---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: 👍 Accepted
date: 2026-11-02
---

# Word count

## Story

When Asha has drafted an article in a plain text editor for a magazine that rejects any
article over 800 words, Asha wants to count its words from the command line, so they can check
it is within the limit before sending it, without pasting it into a website.

## In scope

- Counting the words in one plain text file named on the command line

## Out of scope

- Counting characters or lines
- Reading from standard input

## Requirements

### 1. Count words

WHEN a person runs `wordcount <file>` on a file that exists, the system SHALL print the number of
words in it, where a word is a run of characters that are not whitespace.

| Example | Two words |
|---|---|
| Given | a file holding `hello  world` followed by a newline |
| When | the person runs `wordcount` on it |
| Then | the system prints `2` |

| Example | Empty file |
|---|---|
| Given | an empty file |
| When | the person runs `wordcount` on it |
| Then | the system prints `0` |

#### How we'll check

Unit tests for both examples, run on temporary files.

### 2. Missing file

IF the file named does not exist, THEN the system SHALL print `No such file: <name>` and exit with
status 1.

| Example | File not there |
|---|---|
| Given | no file named `draft.txt` |
| When | the person runs `wordcount draft.txt` |
| Then | the system prints `No such file: draft.txt` and exits with status 1 |

#### How we'll check

A unit test that runs the command on a name with no file behind it.

## Constraints

- None.

## Open questions

- None.
