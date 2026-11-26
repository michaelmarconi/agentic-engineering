---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0064
status: Accepted 👍
date: 2026-11-26
---

# Keep the person's chat messages after a check as their answers

## Question

Which of the person's[^person] messages reach the correction checker[^checker] as their answers to
the questions a check leaves?

## Decision

Chosen: once a correction check has reported, and until the next check starts, the plugin hook[^hook]
keeps the last 20 messages the person writes, word for word and in order, beside the question
tool's answers. A question the tool marks unanswered saves nothing. This holds however the person
answers: by picking an option, by tapping an option on a decision card[^card], or by typing in chat.
The agent asking does nothing for it.

## Background

[ADR 0050](0050-checker-hook-answers.md) has a hook save the person's answers and hand them to the
checker. [ADR 0060](0060-open-findings-check-changed.md) uses those answers to settle a build's open
findings[^finding]. Where there is no question tool, ADR 0050 keeps only the person's next message
after a question that ends with the fixed line "Accept, give your own answer, ignore or defer?".
After a check, this ADR widens that rule to every message; ADR 0050 otherwise stands.

The rule failed in the desktop app. A person typed in chat while the question tool was open, so
the tool returned stand-in text for each unanswered question. That text was saved as their answer,
and their real answer, typed later, was not.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Keep every message the person writes after a check | Chosen | Works however they answer, with no new saved record to track |
| The agent writes the answers into the checker's request | Rejected | A model sometimes rewords what it copies, as [ADR 0050](0050-checker-hook-answers.md) found |
| The agent asks again, ending with the fixed line | Rejected | It depends on the agent writing that line every time, which is what failed |
| Keep chat messages only after a question the tool marks unanswered | Rejected | It needs a waiting record, and misses a later message that changes an earlier answer |

## Consequences

- Good: an answer typed in chat reaches the checker word for word, in builds and documents alike.
- Bad: asides such as "can you simplify that?" reach the checker too, which must tell them from decisions.
- Bad: a long chat between checks makes the checker's request longer, up to 20 messages.

## Out of scope

- The CLI gets no test or trial of its own, though its chat messages are kept too.
- Messages sent before the first check are not kept.

## How we'll check

Applies to: any hook code that saves the person's answers or hands them to a correction checker.

1. A unit test: messages after a check are kept in order, at most 20, and none before it.
2. A unit test: an answer the question tool marks unanswered saves nothing.
3. A unit test: in a project thread[^thread], only the person's own messages are kept.
4. A model-run test case (an eval): a chat reply to an open build finding reaches the next check.
5. A live trial in the desktop app and in a project thread.

## Open questions

None.

## Technical detail

**When.** The message hook (`UserPromptSubmit`) saves a message while the record has been checked
and no later check has started. A build's record clears its answers when a check reports
(`scripts/build_relay.py`); a document's record clears them when a check starts
(`scripts/review_relay.py`). Both stay as they are.

**What.** Each message is saved as `{"question": <the last "**Question N of M: …**" line the agent
wrote, or "(asked in a message)">, "answer": <the message>}`, dropping the oldest past 20. A message
already saved because it answered a decision card, or followed the fixed line, is not saved twice.
In a project thread, a message counts only when its `<message trigger="true">` tag is marked as
written by the person (`from="human"`, `trust="principal"`). Messages from other agents in the
project, and system notices, are left out.

**Unanswered.** The question tool marks a question unanswered with
`annotations[<question>].unanswered`, set to `replied_in_chat`, `skipped` or `dismissed`. Such a
question saves nothing.

[^person]: The person: whoever is using the plugin and answering its questions.
[^checker]: Correction checker: the agent that checks the corrections made after a review, and
    after each round of the person's answers.
[^hook]: Hook: a script the plugin has Claude Code run at set points, such as each time the person
    sends a message.
[^card]: Decision card: a question with buttons that a project thread can post in place of a
    question tool.
[^finding]: Finding: a problem a review reports.
[^thread]: Project thread: a conversation inside a Claude project, one of the places the plugin
    runs.
