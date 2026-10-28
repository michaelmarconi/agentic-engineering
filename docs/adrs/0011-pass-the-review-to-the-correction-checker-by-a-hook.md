---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
date: 2026-10-28
---

# Pass the review to the correction checker by a hook

## Context and Problem Statement

ADR 0010 adds a correction checker after each review. To judge the corrections it needs two texts
exactly as they were: the review report, and the document as it stood when reviewed, before any
correction. The checker starts without the conversation, so something has to hand it both. The
plugin must work in any repository without writing anything into it, so these texts cannot be
saved as files in the person's repository. Only the drafting agent, the Claude running the skill
with the person, sees both texts in the normal course of its work.

## Considered Options

- **The drafting agent pastes both texts into the checker's request.** Rejected: a copy made by a
  model is a rewrite, not a copy. In 30 runs each, a Sonnet drafting agent silently changed a
  line in 2 runs (for example "the two-hour cancellation cut-off" became "the two-hour cut-off").
  An Opus drafting agent copied exactly in all 30, but the drafting model is the person's choice,
  and Opus cost almost twice as much per run. On a longer report the same habit could drop or
  soften a finding, and nothing would notice.
- **Save both texts as files in the person's repository.** Rejected: the plugin must not write
  anything into the repository it is used in.
- **Read them from Claude Code's record of the session on disk.** Rejected: where that record lives
  and what it holds are Claude Code's own details, not documented for plugins, and can change
  without notice.
- **A plugin hook saves both texts and adds them to the checker's request.** A hook is a script
  that Claude Code runs by itself at set moments, such as just before an agent starts, so no
  model copies anything. Before the reviewer starts, the hook saves the document; when
  the reviewer finishes, it saves the report. Both go into the plugin's own data folder, outside
  the repository. Before the checker starts, the hook adds both to the checker's request. It deletes them when the
  checker finishes, or, when no checker runs because the review found nothing, when the session
  ends.

## Decision Outcome

Chosen option: a plugin hook saves both texts and adds them to the checker's request, because it delivered both texts exactly in all 30 of
30 runs, with no permission prompt, using only the hook fields Claude Code documents, and it
writes nothing into the repository.

Because the hook already knows whether a review is on record, it also refuses to start the
checker when no review of that document exists or when the document has not changed since its
review, so a checker never runs before the corrections are made.

### Consequences

- Good: the checker always judges against exactly what the reviewer saw and said, whichever
  model is drafting.
- Good: nothing is written into the person's repository.
- Bad: the plugin gains a hook script to maintain, which depends on Claude Code's documented hook
  fields for agent requests and results; if those change, the hook must follow.
- Bad: the hook approves the checker's start itself, so a permission rule the person set on
  agents does not apply to the checker.
- Bad: a draft that a skill keeps off disk on purpose, such as an issue draft, sits in the
  plugin's data folder until the checker finishes or the session ends.
- Bad: two reviews started at the same moment in one session are not tested, because testing
  that would need timing.

### Confirmation

Applies to: anything one agent of a skill's review hands to another.
Checked by: tests. Unit tests feed the hook recorded events and check what it saves, what it adds
to the checker's request word for word, and when it refuses. Each skill's evals check that the
checker's report quotes a finding from the review report word for word, which only happens if the
hook delivered it.
