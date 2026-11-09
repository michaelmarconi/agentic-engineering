---
type: ADR
status: 👍 Accepted
date: 2026-10-28
---

# Rely on pull requests to record who approved a status change

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. The lifecycle it
defines gives each document a status, and some status changes are a person's decision, such as
accepting an architecture decision record (ADR) or marking a spec, the document that says what
one feature must do, Ready to build. Someone reading a document later may want to know who made
that decision and when, so they can ask them about it.

Git, the version control system, does not reliably say who. Claude makes most of the commits, so
its name is on them: most of the commits on this repository's main branch are by Claude. We have to decide where the record of who approved a status change lives.

We assume that the project puts every change, status changes included, through a pull request:
a proposed change that a person reviews and approves on a code-hosting service such as GitHub
before it is merged into the main branch.

## Considered Options

- **Fields in each document recording who changed its status and when, on every change.**
  Rejected: many changes follow from others or come from automation, such as a spec becoming
  Built when its work is built, so the field would often name a program nobody can ask.
- **Fields recording who signed off and when, only for a person's decisions**, as the MADR
  format for ADRs suggests with its decision-makers field. Rejected: it repeats what the pull
  request already records, and anyone can type any name into it.
- **A field naming the document's owner or author.** Rejected: it does not say who made a given
  decision, and it goes out of date as people move on.
- **The author of the git commit that changed the status.** Rejected: the author is usually the
  agent that made the edit, not the person who decided.
- **No fields in the documents; the pull request that carries the change records who approved it
  and when.** Chosen, below.

## Decision Outcome

Chosen option: no fields in the documents, with the pull request that carries a status change
recording who approved it and when, because the code-hosting service already records the approval
and the merge against people's own signed-in accounts, which a field typed into a document cannot
match.

### Consequences

- Good: documents stay short, with nothing extra to fill in or keep up to date.
- Good: the record of who approved a change cannot be typed in by anyone; it comes from a
  signed-in account.
- Bad: a project that merges changes without pull requests has no record of who decided.
- Bad: to find who approved a status, a reader has to go from the document's history to the pull
  request that changed it, outside the document itself.

### Confirmation

Applies to: the fields of every lifecycle document, and the steps that change a status.
Checked by: inspection. A reviewer of any change to a document's template or to a skill that sets
a status checks that it adds no field recording who made a change or when.
