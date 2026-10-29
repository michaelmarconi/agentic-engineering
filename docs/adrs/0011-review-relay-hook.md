---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Accepted
date: 2026-10-28
---

# Pass the review to the correction checker by a hook

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. The
plugin helps a person write a software project's documents. While Claude writes a document with
the person, we call it the drafting agent. ADR 0010, the architecture decision record before
this one, has
every document reviewed once, corrected once, and then checked by a correction checker. The
reviewer and the checker are agents: separate instances of Claude, each started with its own
instructions, its request, and none of the conversation.

To judge the corrections, the checker compares the document before and after them, against the
review. So it needs two texts exactly as they were: the reviewer's report, and the document as it
stood when reviewed, before any correction. It has neither, since it starts
without the conversation. The drafting agent has both, because it received the report and wrote
the document.

The plugin runs inside other people's projects and must not write anything into them, so the
two texts cannot be saved as files in the project.

## Considered Options

- **The drafting agent copies both texts into its request to the checker.** Rejected: when a
  model copies text, it sometimes rewords it without saying so. We measured this with real
  review reports of 2 to 4 KB and specs of 40 to 110 lines: in each run, a drafting agent had to
  copy one report and one spec into the checker's request, 30 runs per model. With Sonnet, Anthropic's mid-sized model, as the drafting agent, 2 of 30 runs changed a
  line, for example "the two-hour cancellation cut-off" became "the two-hour cut-off". With Opus,
  its largest model, all 30 copies were exact, but the person chooses which model drafts, and an
  Opus run cost almost twice as much as a Sonnet run. In a longer report a reworded line could weaken or lose a
  finding, and no step would detect it.
- **Save both texts as files in the person's project.** Rejected: the plugin must not write into
  the project.
- **Read them from Claude Code's own log of the conversation.** Rejected: where Claude Code keeps
  that log, and what is in it, is undocumented and may change in any release.
- **A hook saves both texts and adds them to the checker's request.** A hook is a script that a
  plugin registers with Claude Code, which runs it automatically at set moments, such as just
  before or just after an agent runs, and lets it change the agent's request. Just before the
  reviewer runs, the hook saves the document. Just after, it saves the report. Both go in a
  folder Claude Code gives each plugin for its own data, outside the project. It keeps one saved copy per
  document, so reviews of different documents never mix. Just before the checker runs, the hook
  adds both texts to the checker's request and approves the checker's start itself. The saved
  texts are deleted when the checker finishes, or at the end of the conversation if no checker
  runs.

## Decision Outcome

Chosen option: a hook saves both texts and adds them to the checker's request, because in 30 runs
both texts reached the checker exactly every time. It needed no approval from the person, used
only hook features that Claude Code documents, and wrote nothing into the project.

### Consequences

- Good: the checker works from exactly what the reviewer saw and reported, whichever model is
  drafting.
- Good: nothing is written into the person's project.
- Bad: the plugin has one more script to maintain, and it depends on the details Claude Code
  gives hooks about each agent's request and reply. If those change, the script must change too.
- Bad: Claude Code normally applies the person's permission rules before an agent starts. The
  hook approves the checker itself, so those rules do not apply to it.
- Bad: some drafts are deliberately never saved as files, such as a bug report that may hold
  private details and that the person has not yet agreed to file. The hook still keeps a copy on
  the person's computer, in the plugin's data folder, until the checker finishes, or until the
  end of the conversation if no checker runs.

### Confirmation

Applies to: any text one agent of a review passes to another.
Checked by: automated tests. Unit tests feed the hook examples of the messages Claude Code sends
it, and check what it saves and what it adds to the checker's request. Tests
that run each skill on sample conversations check that the checker's report quotes a finding
from the reviewer's report word for word, which can only happen if the hook passed it on.
