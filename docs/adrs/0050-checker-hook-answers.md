---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0050
status: Accepted 👍
date: 2026-11-18
supersedes: 0011
---

# Pass the checker the document as last checked and the person's answers by a hook

## Question

How does the checker[^checker] get, word for word, the texts it judges a change against?

## Decision

Chosen: a plugin hook[^hook] saves the document as last checked, the review's reports and the
person's answers to each question, and adds them to the checker's request. It keeps the document
for the conversation, instead of deleting it once the checker finishes as
[ADR 0011](0011-review-relay-hook.md) has it, so the next check can see what changed. It allows a
check with no new review since the last, because a check after the first needs none. A hook's
copies are exact, and nothing is written into the person's project.

## Background

[ADR 0011](0011-review-relay-hook.md) has a hook save the document before a review and the reports
of the reviewer and the language checker, which checks the wording, pass them to the checker, and
delete them once it finishes. [ADR 0049](0049-review-once-check-changes.md) ends each round of the
person's answers with a check of only what changed. That check needs the document as last
checked, which ADR 0011 deletes, and the answers, which nothing saves.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| The drafting agent[^drafting] copies the texts and answers into the checker's request | Rejected | A model sometimes rewords what it copies |
| Compare against the last commit | Rejected | The person commits when they choose, so it may be days old |
| Keep the saved text across conversations | Rejected | It goes stale when someone edits the file by hand |
| The hook keeps the text as last checked for the conversation, and saves the answers | Chosen | Exact copies, kept outside the project, for one conversation |

## Consequences

- Good: each check sees exactly what changed, and exactly what the person said.
- Good: nothing is written into the person's project.
- Bad: the person's answers stay in the plugin's data folder until 30 days after they last
  changed.
- Bad: the hook must change whenever what Claude Code tells hooks changes.
- Bad: the hook approves the checker's start itself, so the person's permission rules do not apply
  to it.

## Out of scope

- A new conversation, where nothing is kept and [ADR 0049](0049-review-once-check-changes.md) has
  a full review run instead.

## How we'll check

Applies to: any text one agent of a review or check passes to another.

1. Test: after a check passes, a second check of a changed document receives the text as last
   checked.
2. Test: the person's answers reach the checker's request word for word.
3. Test: nothing is saved inside the person's project.
4. Test: a record unchanged for 30 days is deleted.

## Open questions

None.

## Technical detail

**What the hook keeps.** One record per document, in the plugin's data folder
(`${CLAUDE_PLUGIN_DATA}`), per conversation: the document as last reviewed or checked, the latest
report from the reviewer and from the language checker, and the person's answers since the last
check. When a check passes or
fails, the record's text becomes the document as it now stands and the answers are cleared; the
reports stay, since a check after the first needs none. The hook no longer refuses a check because
no new review is on record, or because the language checker's report is missing. The record is
deleted once unchanged for 30 days, as now, not when the conversation ends, since a resumed
conversation carries on with it.

**Where answers come from.** After the question tool returns, the hook saves its `answers` map,
which pairs each question's full text with the option the person picked or the text they typed.
Where there is no question tool, as in a Claude project thread, where answers arrive as the
person's messages, it saves the person's next message after each question.

**Evidence that hooks see answers**, tried on 2026-11-18. On Claude Code on a Mac, a hook run after
the question tool received `{"answers": {"<question>": "Green"}}` for a picked option, and
`"Teal — \"bright!\""` for an answer typed into the box, word for word, dash and quotes kept, in
both `tool_input` and `tool_response`. Nothing marks a typed answer as typed: only that it matches
no option. In a cloud session, across two turns, a hook run when the person's message arrives
received the answer message word for word.

**What the checker receives.** The blocks [ADR 0011](0011-review-relay-hook.md) already attaches, with the document as last
checked in place of the document as reviewed, and a new block of the person's answers between
`=== ANSWERS ===` and `=== END ANSWERS ===`.

**Evidence carried from [ADR 0011](0011-review-relay-hook.md).** In 30 runs each, a drafting agent
on Sonnet reworded a line in 2 of 30 copies of a reviewer's report and a document, and one on Opus
in none; the hook's copies were exact in all 30.

[^checker]: The checker is a separate Claude that checks the corrections or answers written into a document after its review.
[^hook]: A hook is a script a plugin registers with Claude Code, which runs it at set moments, such as just before an agent starts, and lets it change the agent's request.
[^tool]: The question tool is the tool Claude Code gives Claude for asking the person a question with listed options and a box to type their own answer.
[^drafting]: The drafting agent is the Claude writing the document with the person.
