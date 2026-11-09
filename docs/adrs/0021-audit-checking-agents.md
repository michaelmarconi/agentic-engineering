---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-05
---

# Check the code against each accepted document with its own fresh agent, all started at once

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. Its
`/audit` skill, a set of instructions Claude follows for one kind of task, finds drift: places
where the code no longer does what an accepted spec says, or no longer follows an accepted ADR (an
architecture decision record, a document that records one technical decision and why it was
made). Accepted here means a person has signed the document off and set its status to
`👍 Accepted`. Checking the code against a document is judgement, so it is done by an agent, a
separate instance of Claude started with its own instructions and none of the conversation.

A project can have dozens of accepted specs and ADRs, and each one may concern a large part of the
code. This record holds one decision: how the checking is split between agents.

## Considered Options

- **One agent checks the code against every document.** Rejected: on a real repository the
  documents and the code they concern don't fit in one agent's context, the text a model can
  attend to at once, so it reads less of each and judges by skimming.
- **One fresh agent per document, started one after another.** Each agent reads only its
  document and the code that document concerns. Rejected: it costs the same in total as starting
  them all at once, since each agent does the same work either way, and a run takes as many times
  longer as there are documents.
- **One fresh agent per document, all started at once.** The same agents, started together;
  the skill gathers their reports when every one has finished. Claude Code allows 20 agents to
  run at once by default, and refuses, rather than queues, any started beyond that: measured on
  2026-11-04 with Claude Code 2.1.318, 25 agents started in one step gave 3 refusals reading
  "Concurrent subagent limit reached". So the skill must start the refused ones again.

## Decision Outcome

Chosen option: one fresh agent per document, all started at once, because each agent then judges
one document with room to read all the code it concerns, and a run takes about as long as its
slowest agent rather than the sum of all of them.

### Consequences

- Good: an agent's judgement of one document is not weakened by having to read other documents
  as well, and its report names only that document's problems.
- Good: a run's length hardly grows with the number of documents, up to Claude Code's limit.
- Bad: more than 20 documents need a second round of agents, started once the first have
  reported, so the skill has to notice refusals and start those agents again.
- Bad: every agent reads part of the code again, so a run that checks every accepted document
  costs roughly one agent's work per document.

### Confirmation

Applies to: the part of `/audit` that checks the code against accepted specs and ADRs.
Checked by: inspection and test. The skill's instructions start one auditor agent for each
accepted document the run checks, all in one step, and start any refused ones again once the
others have reported; the skill's tests on sample repositories check that each accepted document
the run checks got its own agent, and that no other document did.

## Open questions

- None.
