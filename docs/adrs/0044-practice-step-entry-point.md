---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-17
supersedes: 0041
---

# Record each practice step as a named entry point, and anything more as a script

## Question

A step is anything a project's practices[^practices] tell an agent to run. Which steps may the
practices record unchanged, and where does every other step go?

## Decision

Chosen: a step is recorded unchanged only when it is one unattended line, reporting failure by its
exit code, that calls a named entry point with nothing but values the running skill[^skill] fills
in. A named entry point is a command runner entry, such as a Make target, a script in the project's
scripts folder, or a tool's standard command. That standard command may carry the argument the
tool's documentation gives as usual. Every other step becomes a script in the scripts folder,
which the practices name. The practice records the runner entry calling the script, or, with no
runner, the script itself. This is chosen because the project's own choices then live in a file
that tests can run, while common commands stay short.

## Background

[ADR 0041](0041-practice-step-command.md) made every step one line that calls one program, kept in a
runner or one scripts folder. It judged a step only by its form, so a long line holding a project's
settings, folders and accounts passed unchanged. Nothing tests such a line, so it falls out of
date unnoticed, even when it changes real data.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Any one-line command, as [ADR 0041](0041-practice-step-command.md) allows | Rejected | A long line of the project's own choices goes untested |
| A script for every step | Rejected | Wraps a tool's standard test command in a file that adds nothing |
| A script when a step has more than a few arguments | Rejected | Any limit is arbitrary |
| A script when a step touches a real outside service | Rejected | Misses choices that touch nothing outside |
| Named entry points recorded unchanged, anything else as a script | Chosen | The project's choices always sit in a script, and common commands stay short |

## Consequences

- Good: the project's own choices for a step sit in one script, which tests can run.
- Good: any project can follow it, since a scripts folder needs no tool.
- Bad: a project gains small scripts for steps once written on one line.
- Bad: practices recorded earlier may break this rule until updated.

## Out of scope

- Who writes the scripts and whether they need tests: decided in [ADR 0045](0045-practices-skill-writes-scripts.md).
- Which runner a project uses, if any: the project's own practice.
- Commands no practice records.

## How we'll check

Applies to: every command the practices skill records, and the plugin's start-of-session rules for Claude.

1. Test: the practices check script passes a named entry point with only values the skill fills in, and fails chained commands.
2. Test: asked to record a long command holding the project's settings, the practices skill records a script.
3. Inspection: the practices skill's checklist of pass-or-fail checks fails a recorded command that passes the project's own choices as arguments.
4. Inspection: those rules state the rule once.

## Open questions

- None.

## Technical detail

**A step** is anything a practice tells an agent to carry out by running something, as in
[ADR 0041](0041-practice-step-command.md).

**A recorded command** is one line, run from the repository root, that:

- calls one named entry point, such as `make test`, `pnpm check:new-mail`, `script/deploy`,
  `npm test`, `pytest` or `cargo build`;
- passes it nothing but `{name}` values, such as `pytest {file}` or `script/deploy {environment}`;
- holds no `&&`, `||`, `;`, `|`, `&` or line break outside quotes;
- needs no answer from a person, and exits 0 on success and non-zero on failure.

**A tool's standard command** is the program and subcommand the tool documents for a job, such as
`npm test`, `pytest`, `cargo build` or `go test ./...`, where `./...` is the argument Go's
documentation gives for testing every package.

**Everything else**, such as flags the project chose, settings, folder or account names, or several
commands in a row, goes into a script in the project's scripts folder, such as `script/check-new-mail`.
When the project has a runner, a runner entry that calls only the script is recorded, such as
`"check:new-mail": "script/check-new-mail"` in `package.json`, recorded as `pnpm check:new-mail`.

**Example.** `docker exec mail-test doveadm -o mail_driver=imapc copy -u test 'Test Folder' mailbox INBOX all`[^doveadm]
is not recorded unchanged: its options, user and folder are the project's choices, so they move
into `script/check-new-mail`.

**Checking.** The practices check script fails a line that chains commands, and lists any argument
other than a `{name}` value after the program and its subcommands, for the skill to judge. The
practices skill's checklist fails a recorded command that passes the project's own choices.

[^practices]: Practices are the project's recorded ways of doing things, one topic at a time, in a short section of `AGENTS.md` and files under `docs/practices/`.
[^skill]: A skill is a set of instructions Claude follows for one step, started as a slash command such as `/agentic:practices`.
[^doveadm]: `doveadm` is the administration command of the Dovecot mail server; `imapc` is its setting for reading mail from another IMAP server.
