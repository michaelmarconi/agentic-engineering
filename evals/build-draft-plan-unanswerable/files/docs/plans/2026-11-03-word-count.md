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

### 1. Which character encoding the writers' files use

The writers' editors may save files in different encodings, and reading with the wrong one fails
or miscounts.

> **Proposed:** Only the person can say: a sample of the writers' files, or knowing which editor
> they use, would settle it.
>
> **Why:** Nothing in the specs, ADRs or code says which encoding the files are in.
