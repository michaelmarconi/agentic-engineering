---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Spec
status: 👍 Accepted
date: 2026-11-10
---

# Greeting

## Story

When someone runs the greeter with their name, they want to be greeted by name.

## In scope

- Greeting one person.

## Out of scope

- Other languages.

## Requirements

### 1. Greet by name

When someone runs `python3 greet.py <name>`, the tool SHALL print `Hello, <name>!`.

| Example | Greets Ada |
|---|---|
| Given | nothing |
| When | someone runs `python3 greet.py Ada` |
| Then | it prints `Hello, Ada!` |

#### How we'll check

Test.

## Constraints

- None.

## Open questions

- None.
