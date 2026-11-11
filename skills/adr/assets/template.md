---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: <YYYY-MM-DD>
---

# <The decision in plain words, such as "Keep session data in Redis"; the question while no option is chosen>

## Question

<The one choice to make, in one to three sentences, such as "Where does the service keep session data?">

## Decision

Not chosen yet; see Open questions.
<!-- Once the person picks: "Chosen: <the option in full>, because <the reason, in at most two sentences>." A `mermaid` diagram of the chosen option may follow, only if the person picks one at hand-over. -->

## Background

<What forces the choice now, in one short paragraph a newcomer can follow. Name each earlier ADR it builds on by number, linked to its file, such as `[ADR 0003](0003-message-queue.md)`, with what it decided in a few words.>

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| <Option> | <Open before the choice; then Chosen or Rejected> | <One line: the main trade-off, or why it was chosen or rejected> |

## Consequences

- Good: <one line>
- Bad: <one line>

## Out of scope

- <Each limit (something not covered that would not change the choice) or decision left to another ADR, stated once; or "None.">

## How we'll check

Applies to: <the concern, such as "any code that stores or reads session data">.

1. <One check, by test, demonstration, inspection or analysis, in one line>

## Open questions

- <What only the person can settle, ending "Proposed:" and the answer you would choose (or, if only the person can know, what would settle it), or "None.">

## Technical detail

<The exact mechanism, rules and settings; evidence, such as a spike's measurements, in this ADR's own words; each check in full where one line was not enough. Or "None.">
