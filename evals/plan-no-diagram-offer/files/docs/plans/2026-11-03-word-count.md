---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Plan
status: 📝 Draft
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

Add `src/wordcount.py`, whose `main` prints the number of words in the file named on the command
line, or the missing-file message. Tests for both requirements go in `tests/test_wordcount.py`.
Build "Count words" first, then "Missing file".

## Open questions

- None.
