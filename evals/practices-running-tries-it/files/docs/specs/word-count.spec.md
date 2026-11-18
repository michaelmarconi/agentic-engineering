---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: Accepted 👍
date: 2026-11-10
---

# Word count

## Story

When a writer has a draft, they want to count its words, lines or a web page's words from the
command line, so they can keep to a word limit without opening an editor.

## In scope

- Text files and web pages.

## Out of scope

- Word processor files.

## Requirements

### 1. Count the words in a file

When the writer runs `bin/wordcount <file>`, the tool SHALL print the number of words in the
file, words being runs of characters between spaces or line breaks.

| Example | Three words |
|---|---|
| Given | a file holding `the cat sat` |
| When | the writer runs `bin/wordcount` on it |
| Then | it prints `3` |

#### How we'll check

Test.

### 2. Count the lines in a file

When the writer runs `bin/wordcount --lines <file>`, the tool SHALL print the number of lines in
the file.

| Example | Three lines |
|---|---|
| Given | a file holding three lines, `one`, `two` and `three`, each ending in a line break |
| When | the writer runs `bin/wordcount --lines` on it |
| Then | it prints `3` |

#### How we'll check

Test.

### 3. Count the words in a web page

When the writer runs `bin/wordcount --url <address>`, the tool SHALL fetch the page and print the
number of words in its text.

| Example | A short page |
|---|---|
| Given | the page stand-in serving the page `/hello`, whose text is `hello web world` |
| When | the writer runs `bin/wordcount --url http://localhost:8765/hello` |
| Then | it prints `3` |

#### How we'll check

Test.

## Constraints

- None.

## Open questions

- None.
