---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-02
supersedes:
superseded-by:
---

# Keep the log in a text file

## Question

Where is the reading log stored, so that the reader can read it without the tool?

## Decision

Chosen: a plain text file, one book per line, because the reader can open it in any editor.

## Background

The log must stay readable without the tool.
