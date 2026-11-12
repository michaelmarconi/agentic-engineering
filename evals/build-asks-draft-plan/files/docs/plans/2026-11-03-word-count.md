---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Plan
status: 📝 Draft
date: 2026-11-03
---

# Count the words in a file

## Specs

- [Word count](../specs/word-count.spec.md)
  - [Count words](../specs/word-count.spec.md#1-count-words)
  - [Missing file](../specs/word-count.spec.md#2-missing-file)

## ADRs

| ADR | Decision |
| --- | --- |
| [0001](../adrs/0001-standard-library-only.md) | Use only Python's standard library |

## Decisions

- The command is a Python module run as `python3 -m src.wordcount <file>`: the tool is copied as
  a folder, so a module needs no install step.

## Plan

Writers need a word count without a word processor; this builds the whole spec.

Add `src/__init__.py` and `src/wordcount.py`, with a function that counts the words in a text and
a `main` that reads the file named on the command line, prints the count, and handles a missing
file. Tests go in `tests/test_wordcount.py`, using temporary files and running `main` directly.
Build "Count words" first, then "Missing file".

## Open questions

### 1. Which stream gets the missing-file message

The spec says the message is printed, not where.

> **Proposed:** Print `No such file: <name>` to standard error.
>
> **Why:** Standard output then holds only counts, so scripts can read it.

### 2. Whether to read the file at once or line by line

Articles are short, but a file could be large.

> **Proposed:** Read the whole file at once.
>
> **Why:** The files are articles of a few thousand words, and it is simpler.
