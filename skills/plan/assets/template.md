---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Plan
status: 📝 Draft
date: <YYYY-MM-DD>
---

# <The piece of work, in plain words>

## Specs

<!-- Each spec this work builds, with the requirements it delivers nested beneath it, each a
     link to its heading in the spec: its name exactly as in the spec, without the number, and
     the anchor GitHub gives the heading, as #2-reply-to-all for "### 2. Reply to all". Only
     these. "None." if the work only follows ADRs. -->
- [<Spec title>](../specs/<capability>.spec.md)
  - [<Requirement name, as in the spec>](../specs/<capability>.spec.md#<heading-anchor>)

## ADRs

<!-- Each decision the code must follow, as a row: its number as the link, and its title,
     word for word, as the decision. "None." instead of the table if there are none. -->
| ADR | Decision |
| --- | --- |
| [<NNNN>](../adrs/<NNNN-subject>.md) | <The ADR's title> |

## Decisions

<!-- One line for each technical decision agreed with the person whose reason nobody needs once
     the work is built, or only someone changing that code later, in which case the line says
     /build leaves the reason as a comment beside the code: what was decided and why, including
     keeping the work as one plan when the practices say to split it. A decision later work must
     follow is an ADR, one a user or caller relies on is a spec change, one every piece of work
     follows is a practice: each an open question. "None." if there were none. -->
- <What was decided>: <why>

## Plan

<!-- How the work will be done, with subheadings and length to suit it. Start with why the work
     is being done and what it leaves for later. Give one recommended approach. Name the files
     that matter and the existing code to reuse; describe a repeated pattern once. No code, and
     no decision that is not under Decisions or ADRs. A diagram the person picks at the hand-over
     goes after this opening paragraph, as a mermaid block. -->

## Open questions

<!-- Each question ends "Proposed:" and the answer you would choose (or, if only the person
     can know, what would settle it). "None." before `🟢 Ready to build`. -->
- None.
