---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-16
supersedes: 0031
---

# Check how much conversation a session has gained before a build, and ask the person when it is a lot

## Question

What must be true of a session[^session] before a build[^build] starts in it, and what happens
when it is not?

## Decision

Chosen: when a build is asked for, the plugin measures how much conversation the session has
gained since Claude's first reply; under 20,000 tokens[^token] the build starts, and over it Claude
asks the person[^person] whether to build here anyway or start a new session, because this measures directly what could
make a build follow the conversation instead of the plan, and the person can judge the rest.

## Background

A build should start from the written plan[^plan], not from a long conversation that could steer it.
Today a hook[^hook] allows a build only in answer to the person's first message in a new or cleared
session. [ADR 0031](0031-build-session-start.md) has the refusal tell the person how to start a new
session with the plan. In a Claude project thread[^thread] that another Claude session, the coordinator[^coordinator],
opens, no message counts as the person's, so every build is refused. A thread that has already done
work is let through once the person writes.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Keep counting the person's messages | Rejected | Refuses every thread the coordinator opens |
| Allow a build only before any tool has run | Rejected | Claude often uses a tool first, such as posting progress, so sessions with no earlier conversation would be refused |
| Allow a build only in the session's first turn | Rejected | Still refuses a session holding only a short exchange |
| Measure the conversation gained, and refuse over a limit | Rejected | A refusal blocks a person who knows the session is fine |
| Measure the conversation gained, and ask the person over a limit | Chosen | Works wherever the plugin runs, and leaves the call to the person |

## Consequences

- Good: a thread the coordinator opens can build at once.
- Good: a session with a short exchange before the build needs no new session.
- Good: a long planning conversation still gets a warning before the build.
- Bad: a person can choose to build in a session with a long earlier conversation.
- Bad: the measure depends on a record Claude Code keeps but does not document.

## Out of scope

- Starting a new session for the person: the plugin still only tells the person how to start one.

## How we'll check

Applies to: anything that decides whether a build starts, or tells the person how to start one.

1. Test: unit tests measure growth from sample session records, including one with no reply and one compacted[^compact].
2. Test: unit tests check the hook never refuses a build, typed or asked for in words.
3. Test: a sample conversation under the limit starts the build without asking.
4. Test: a sample conversation over the limit asks once, and "Start clean" gives both steps with the plan's path.
5. Demonstration: in a thread the coordinator opens, a build starts.

## Open questions

- None.

## Technical detail

**The measure.** Claude Code writes each session's record to the file it passes every hook as
`transcript_path`. Each of Claude's replies in it carries `message.usage`; the context in use is
`input_tokens + cache_read_input_tokens + cache_creation_input_tokens`. Lines with `isSidechain`
true belong to sub-agents and are skipped. Growth is the latest reply's figure minus the first
reply's. With no reply yet, growth is 0. After compaction the latest figure is smaller, so the
session is measured as it now stands. A session whose record cannot be read is measured as
having gained nothing, because the question only warns the person and does not stop the build. A
PreToolUse hook sees the record one reply behind, so growth can be understated by one reply; for a
warning that is close enough.

**The limit.** 20,000 tokens, agreed with the maintainer. It sits below the smallest session that
wrote a plan, about 31,000, so planning in the same session is always caught. It is set low on
purpose: over the limit the person is only asked, so a question after a first turn spent reading
code costs one answer.

**The hook.** `scripts/fresh_session.py` stops refusing and stops counting messages. When the build
skill starts, or the person types `/build` or `/agentic:build`, it records that a build is running,
for the check that refuses commits and pushes on the default branch during a build, as now. It also measures growth and passes the figure, and whether it is over
the limit, to Claude as added context (`additionalContext`, on PreToolUse and UserPromptSubmit).

**The build skill.** Its first check reads that figure. Over the limit, it asks one question,
with the choices "Build here anyway" and "Start clean", on Claude Code's multiple-choice question
tool (AskUserQuestion). "Start clean" ends the run and gives the two steps, with the plan's path
filled in: run `/clear`, then send `/agentic:build <path to the plan>`; in a Claude project thread,
which has no `/clear`, open a new thread and send that command as its first message. The plugin
never starts a session itself, for the reasons [ADR 0031](0031-build-session-start.md) gives.

**Evidence, measured on 2026-11-16.**

- A thread the coordinator opened recorded no message from the person.
- Its first reply used about 85,000 tokens, and a terminal run's about 49,000, so only growth compares across places.
- Growth was about 25,000 after a first turn spent reading code, and about 43,000 after a design discussion.
- Earlier sessions that wrote documents grew by about 31,000 for one plan, 76,000 for a brief and part of a spec, and 135,000 for four documents.
- All 37 desktop-app sessions and one terminal session on the maintainer's computer carried the usage figures.
- In a terminal run (Claude Code 2.1.325), the added context reached Claude, and the figure seen by a PreToolUse hook lagged one reply behind.

[^session]: A session is one conversation with Claude Code, from its start or from the last `/clear`, which empties it.
[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed by separate Claude agents.
[^token]: A token is the unit Claude measures text in; 20,000 tokens is roughly 15,000 words.
[^person]: The person is whoever is working with Claude and the plugin on the project.
[^plan]: A plan is the plugin's document that sets out one piece of work; once the person signs it off, it is ready to build.
[^hook]: A hook is a script Claude Code runs automatically at set moments, here when the person sends a message and when Claude starts a skill.
[^thread]: A Claude project thread is one conversation inside a project in the Claude app, where each piece of work gets a thread of its own.
[^compact]: Compaction is when Claude Code replaces a long conversation with a shorter summary, which makes the session smaller.
[^coordinator]: The coordinator is the Claude session that talks with the person in a project's main chat and opens its threads.
