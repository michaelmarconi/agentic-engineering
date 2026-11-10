---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Plan
status: 📝 Draft
---

# Count the words in a file

## Specs

- [Word count](../specs/word-count.spec.md)
  - Requirement: Count words
  - Requirement: Missing file

## ADRs

- [0001 Use only Python's standard library](../adrs/0001-standard-library-only.md)

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

- None.
