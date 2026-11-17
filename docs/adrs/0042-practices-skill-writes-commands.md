---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: ↪️ Superseded
date: 2026-11-17
superseded-by: 0045
---

# The practices skill writes the one-line commands it records, from steps the person agreed

## Question

When a step the practices[^practices] need has no single command yet, which part of the plugin
writes that command into the project's command runner or scripts folder?

## Decision

Chosen: the practices skill[^skill] writes the command for a step, during its interview[^interview]
with the person, where the person agrees that step. The skill may add or change an entry in the
project's command runner or scripts folder, only to run agreed steps in order. It shows the
entry and tries its safe parts. Then it records the one-line command in the project's practices.
When a step needs an entry and the project has neither, it creates one the same way. The release
and deploy skills[^release] write nothing; when a command is missing, they say which and point to the practices skill.
This is chosen because the interview is where the steps are worked out, so only one skill writes the
project's commands.

## Background

[ADR 0041](0041-practice-step-command.md) requires every practice step to be one command, kept in
the project's command runner or scripts folder. For setting up, testing and running the product, such
commands nearly always exist already. For releasing and deploying, the steps are often agreed for
the first time in the practices interview, so something must turn them into a command.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| The practices skill, during the interview | Chosen | The steps are agreed there, and only one skill writes the commands |
| The build[^build] skill, through a plan[^plan] | Rejected | Combining agreed steps is not building the product, and needs a plan for a few lines |
| The skill that needs the command, such as the release skill, on its first run | Rejected | Every such skill would write commands, spreading them across skills |

## Consequences

- Good: a person agrees how to release or deploy and gets a working command in the same conversation.
- Good: no skill but the practices skill adds to the project's commands outside a build.
- Bad: the practices skill now edits files beyond the practices, so it must show each change first.
- Bad: an entry it writes is not reviewed for bugs as a build's code is.

## Out of scope

- Commands with real program logic, such as retries or conditions: those are ordinary product work for a plan and a build.
- Which runner a project uses: the person chooses it when the practices skill asks.

## How we'll check

Applies to: the practices skill and every skill that runs recorded commands.

1. Test: asked to record a release made of several commands, the practices skill shows a new runner entry, then records the one-line command.
2. Test: with no runner or scripts folder, the practices skill asks which to create before writing anything.
3. Test: the release skill, with no recorded release command, writes nothing and names the practices skill.
4. Inspection: only the practices skill's instructions allow it to add a runner entry or script outside a build.

## Open questions

- None.

## Technical detail

**Combining only.** An entry the practices skill writes runs, in order, the commands the person agreed
in the interview, keeps any placeholder written `{name}` in the recorded step, for the skill that runs the step to fill in, and stops at the first failure with
a non-zero exit code.

**Showing and trying.** The skill shows each new or changed entry before writing it. It runs only
the safe parts the interview marks safe, such as reading the current version or a dry run, never a
real release, deploy or rollback.

**Creating the place for commands.** The skill asks whether the person wants a command runner, and
which one, or one scripts folder, and proposes the tool the project's language already provides
where there is one, such as the scripts of `package.json`.

[^skill]: A skill is a set of instructions Claude follows for one step, started as a slash command such as `/agentic:practices`.
[^interview]: The practices skill's interview is the conversation in which it asks the person how the project does things, one topic at a time.
[^release]: The release and deploy skills are planned skills of this plugin that release a new version of the product and deploy it to an environment.
[^practices]: Practices are the project's recorded ways of doing things, one topic at a time.
[^plan]: A plan is the plugin's document for one piece of work that builds part of a spec.
[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed.
