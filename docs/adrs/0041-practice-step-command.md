---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: ↪️ Superseded
date: 2026-11-17
superseded-by: 0044
---

# Record each practice step as one command, kept in the project's one place for commands

## Question

How should a project's practices[^practices] record the commands that skills[^skill] and agents run,
such as setting up, testing, releasing and deploying?

## Decision

Chosen: every step a practice tells an agent to carry out by running something is recorded as one
command, and anything longer lives as a named entry in the project's one place for commands: a
command runner, such as Make, or a single scripts folder, which the practices name. A one-line command needs no entry there. This is chosen because every skill can then run one line and read one pass or fail,
without making any one tool compulsory.

## Background

Practices record commands topic by topic, with nothing saying what a command may be. A step can be
written as several commands and edits in prose, which each skill then has to interpret, and the
prose then stops matching what the project really runs. The release and deploy skills now being designed run
recorded steps that change real systems, so each step must be exact. Projects with no rule on where
commands live also tend to end up with scripts scattered across many folders.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Record whatever commands each topic needs, as today | Rejected | Written steps stop matching what the project runs, and skills must interpret prose |
| Require every project to use a command runner | Rejected | Forces one tool on every project the plugin is used in |
| One command per step, kept in a runner or one scripts folder | Chosen | Exact steps for every skill, with the project free to choose the tool |

## Consequences

- Good: every skill runs a recorded step the same way and reads its result from the exit code.
- Good: a project's repeatable steps sit in one place instead of scattered scripts.
- Bad: a project with long steps must turn each into a runner entry or script before it can be recorded.
- Bad: practices recorded before this decision may break the one-command rule until they are brought up to date.

## Out of scope

- Which runner a project uses: that is the project's own practice, or its own ADR[^adr] if it weighs alternatives.
- Who writes runner entries and scripts, and who creates the runner or scripts folder: decided in [ADR 0042](0042-practices-skill-writes-commands.md).
- Commands a person runs by hand that no practice records.

## How we'll check

Applies to: every command the practices skill records, and the rules the plugin gives Claude at each session start.

1. Test: the practices check script passes a one-line command and fails one that chains, pipes or spans lines.
2. Test: the practices skill never records a step of several commands as one line.
3. Inspection: the practices skill requires each recorded command to run unattended and report failure by its exit code.
4. Inspection: the plugin's session-start rules state the rule once, and the practices skill's checks include it.

## Open questions

- None.

## Technical detail

**A step** is anything a practice tells an agent to carry out by running something, such as setting
up a fresh copy, running all tests, running one test file, linting, starting or stopping the
product, releasing, deploying, rolling back or checking a deploy.

**A command** is one line, run from the repository root, that calls one program and:

- takes only arguments, where `{name}` marks a value the skill fills in, such as `{file}` or `{environment}`;
- holds no `&&`, `;`, `|` or line break;
- needs no answer from a person while it runs;
- exits 0 on success and non-zero on failure.

So `make test`, `npm test`, `script/deploy {environment}` and `pytest {file}` qualify, while
`npm ci && npm run build`, or "run the migrations, then restart the server", do not.

**The project's one place for commands** is either a command runner (a Makefile, a justfile, the
scripts of `package.json` or another tool's equivalent) or one scripts folder, such as `script/`
with names like `script/setup` and `script/test`, as in GitHub's "Scripts to Rule Them All"
convention (https://github.blog/engineering/scripts-to-rule-them-all/). The practices name which,
in one line.

**Checking.** The practices skill's check script tests each recorded command against the rules
above, and the practices skill's list of checks fails a step recorded any other way.

[^practices]: Practices are the project's recorded ways of doing things, one topic at a time, in a short section of `AGENTS.md` and files under `docs/practices/`.
[^skill]: A skill is a set of instructions Claude follows for one step, started as a slash command such as `/agentic:practices`.
[^adr]: An ADR (architecture decision record) is a document recording one technical decision and why it was made.
