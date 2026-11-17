---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: Accepted 👍
date: 2026-11-17
supersedes: 0042
---

# The practices skill writes scripts without logic, and a build writes the rest

## Question

Which part of the plugin writes the scripts a project's practices[^practices] call, and which of
those scripts need tests?

## Decision

Chosen: the practices skill[^skill] writes only scripts without logic, meaning no condition, loop,
retry or reading of output, and leaves the rest to a plan[^plan] and a build[^build]:

- It writes a script that runs, in order, the commands the person agreed for a step, one recorded
  action such as running the tests. The project's settings, such as paths, are filled in. It shows
  each script first, creating a scripts folder if there is none, adds a runner entry calling it
  when there is a runner, and runs it only where that changes nothing real.
- A script that needs logic, or a change adding logic to one, is not written: its step is recorded
  with no command yet, and the skill's closing message names it as work for a plan and a build.
- A script that changes a real outside service gets a test suggested in that message, never
  written or waited for.
- The release and deploy skills still write nothing.

This is chosen because code with logic gets the tests and review that code gets, while a script
without logic adds no process and its one risk is named for the person.

## Background

[ADR 0042](0042-practices-skill-writes-commands.md) let the practices skill write command runner
entries, such as Make targets, combining agreed steps. [ADR 0044](0044-practice-step-entry-point.md) now
sends every step that is more than one plain command into a script. A script that changes real
data and is never run against a test copy[^stand-in] of the service can break unnoticed.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Every script through a plan and a build | Rejected | Too much process for a few lines |
| The practices skill writes each script and its tests, tests first | Rejected | Duplicates the build's steps |
| The practices skill writes scripts without logic; a build writes the rest | Chosen | No new steps; code with logic still gets tests and review |

## Consequences

- Good: every script with logic is built tests first and reviewed.
- Bad: a script that changes a real outside service has no test unless the person asks for one.
- Bad: a script unsafe to run is recorded untried.
- Bad: the skill creates a scripts folder without asking, where [ADR 0042](0042-practices-skill-writes-commands.md) asked.

## Out of scope

- Which steps need a script: decided in [ADR 0044](0044-practice-step-entry-point.md).
- Which command runner a project uses.

## How we'll check

Applies to: the practices, release and deploy skills.

1. Test: given several commands as one step, the practices skill shows a script, then records it.
2. Test: given a step with a retry, the practices skill writes no script and names the work for a plan.
3. Test: given a step changing a real outside service, the practices skill does not run it and suggests a test.
4. Inspection: only the practices skill's instructions allow it to write a script outside a build.

## Open questions

- None.

## Technical detail

**A script without logic** runs, in order, the commands the person agreed, with the project's
settings, such as paths and names, filled in. It passes on any value the step takes through a
`{name}` placeholder, such as `{environment}`, and stops at the first failure with a non-zero exit
code. It holds no condition, loop, retry or parsing of output.

**The scripts folder.** When a step needs a script and the project has no scripts folder, the skill
creates `script/`, unless the project already names another, and shows it with the first script.
When the project has a command runner, the skill also adds an entry that calls only the script.

**Trying.** The skill runs a new or changed script only when everything it touches is in the
repository or among the test copies the project's practices list as safe to run against. It never
runs a real release, deploy or rollback, nor anything that changes a real outside service. Its
closing message names each script it did not run, and why.

**Logic.** A step that needs logic is recorded in the practice as a step with no command yet, and
the closing message names the script as work for `/agentic:plan`. A request to add logic to an
existing script is passed on the same way.

**Suggested test.** For a script that changes a real outside service, the closing message names a
test, as work for `/agentic:plan`, that runs the script against the service's test copy.

**Release and deploy skills.** As under [ADR 0042](0042-practices-skill-writes-commands.md), when a
command is missing they say which and point to the practices skill.

[^practices]: Practices are the project's recorded ways of doing things, one topic at a time, in a short section of `AGENTS.md` and files under `docs/practices/`.
[^skill]: A skill is a set of instructions Claude follows for one step, started as a slash command such as `/agentic:practices`.
[^plan]: A plan is the plugin's document for one piece of work, saying how it will be done.
[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed.
[^stand-in]: A test copy of an outside service, such as a local mail server, runs on the developer's machine and cannot change anything real.
