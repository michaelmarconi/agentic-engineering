---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-12
---

# Tell the person the two steps to start a build, rather than starting a session for them

## Question

When the person[^person] asks for a build[^build] partway through a session, how does the build get
the new session it needs?

## Decision

Chosen: the plugin never starts a session itself; whenever it refuses to start a build, and whenever a
plan[^plan] is signed off as ready to build, it tells the person it has no reliable way to start a
session, then gives the exact two steps: `/clear`[^clear], then the build command, `/agentic:build`, with that plan's path. In a Claude project thread[^thread], which has no
`/clear`, the second step alone is typed as the first message of a new thread. No way of starting a
session works everywhere the plugin runs, while those two steps do.

## Background

A build starts only in answer to the first message of a session, or the first after `/clear`, so it
begins with a clean context and the written plan. A hook[^hook] enforces this. When a person signed a
plan off and asked for the build in the same session, the hook refused with only "start a new
session", and Claude's attempt to start one was blocked by a permission check. The person who ran into
this asked the plugin to start the session itself.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Start a new session with the build as its first message, through a session-starting tool the Claude app provides | Rejected | Claude Code in a terminal has none, and a permission check can block one where it exists |
| Run the build in a second Claude agent started from the current session | Rejected | That agent cannot start the agents that review the build's work |
| Drop the rule and build in the current session | Rejected | The build would start from the planning conversation, not the written plan |
| Keep the rule, and give the exact two steps wherever the person might ask | Chosen | Works wherever the plugin runs, leaving the person nothing to figure out |

## Consequences

- Good: the person gets the exact commands for that plan.
- Good: the plugin depends on nothing that only some apps provide.
- Bad: the person still takes two steps, where the person who ran into this asked for none.

## Out of scope

- Whether a build may start partway through a session, which stays as it is.
- A future way to start sessions everywhere, which would need a new ADR.

## How we'll check

Applies to: anything that refuses to start a build or tells the person how to start one.

1. Test: unit tests check that the hook's refusal gives the reason, `/clear`, the build command and what to do in a Claude project thread.
2. Test: a sample conversation asks for a build partway through a session and checks the reply gives both steps with the plan's path, and starts no session.
3. Test: a sample conversation signs a plan off and checks the reply ends with both steps for that plan.

## Open questions

- None.

## Technical detail

**The hook.** `scripts/fresh_session.py` keeps its rule unchanged. Its refusal, given both when a
typed `/build` or `/agentic:build` is blocked and when the build skill is refused, says the plugin has no reliable way to start a session for
the person, then: run `/clear`, then `/agentic:build <path to the plan>`; in a Claude project thread, open a new thread
and send `/agentic:build <path to the plan>` as its first message. The hook does not know which
plan was meant, so the refusal holds a placeholder, and Claude fills in the path when it passes the
reason on.

**The build skill.** When the hook refuses, the skill passes the two steps on with the plan's path
filled in, and never tries to start a session in any other way.

**The plan skill.** Once a plan's status is set to `🟢 Ready to build`, the reply ends with the same
two steps, naming that plan's path.

**Why a separate Claude cannot run the build.** A Claude agent started through another session's
Agent tool (the Claude Code tool for starting a sub-agent) has no such tool itself, so it cannot
start the build's reviewers.

[^person]: The person is whoever is working with Claude and the plugin on the project.
[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed by separate Claude agents.
[^plan]: A plan is the plugin's document that sets out one piece of work; once the person signs it off, it is ready to build.
[^clear]: `/clear` is the Claude Code command that empties the current session.
[^thread]: A Claude project thread is one conversation inside a project in the Claude app, where each piece of work gets a thread of its own.
[^hook]: A hook is a script Claude Code runs automatically at set moments, here when the person sends a message and when Claude starts a skill.
