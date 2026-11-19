---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0051
status: Draft 📝
date: 2026-11-19
supersedes: 0033
---

# Keep every file the plugin writes outside the repository in the session's scratchpad

## Question

Where does the plugin write the files it keeps outside the repository: the reports a build[^build],
an audit[^audit] or a verify run[^verify] ends with, and the records its hooks keep during a session?

## Decision

Chosen: the session's scratchpad[^scratchpad], for every file the plugin writes outside the
repository, kept only as long as Claude Code keeps that folder. It is the one folder the person can
open in every app, and a report is read once, soon after its run.

## Background

[ADR 0033](0033-end-of-run-report.md) put the end-of-run reports in the plugin's data
folder[^data]. The Claude Code desktop app opens only files in the session's own folders, so the
person cannot open a report from the reply. ADR 0033 rejected the scratchpad because no step of the plugin could
state its path; Claude and every hook are now told it.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| The data folder, as now | Rejected | The desktop app cannot open it |
| The data folder, plus a copy of each report in the scratchpad | Rejected | Two copies of every output |
| The person's repository | Rejected | The plugin writes there only its own planning documents and the project's rules for agents |
| The data folder, with a command that opens the report | Rejected | A desktop user has to use a terminal |
| The scratchpad, for every file | Chosen | One place, which every app can show |

## Consequences

- Good: the person opens the report from the reply in the terminal, the desktop app and a project thread[^thread].
- Good: every output is in one place, and the plugin clears out only old review records, as [ADR 0050](0050-checker-hook-answers.md) says.
- Bad: a report is gone once the scratchpad is cleared; a copy attached in a project thread stays.
- Bad: scripts depend on Claude passing them the path, so they refuse one that cannot be this session's.
- Bad: untested, at the person's word: that the desktop app opens files in the scratchpad rests on one user's report.

## Out of scope

- Sessions with no scratchpad: they get the system's temporary folder, as tests do today.
- The decisions of [ADR 0034](0034-report-copied-by-script.md), [ADR 0040](0040-verify-built-product-outside.md) and [ADR 0050](0050-checker-hook-answers.md), which stand: only the folder they name changes.
- How a file is shown to the person, which [ADR 0025](0025-document-review-display.md) decides.
- How reports are copied into the file, which [ADR 0034](0034-report-copied-by-script.md) decides.
- Accepting a build whose reviews' corrections failed their check, which [ADR 0052](0052-ask-accept-open-findings.md) decides.

## How we'll check

Applies to: any code that writes or reads a file the plugin keeps outside the repository.

1. Test: a sample build, audit and verify each write their report in the given scratchpad only.
2. Test: each hook keeps its records in the scratchpad it is given, and none in the data folder.
3. Test: a script refuses a scratchpad path that does not end in this session's folder.
4. Inspection: no code in the plugin names its data folder.

## Open questions

None.

## Technical detail

**The folder.** Claude Code gives each session a scratchpad at
`<temp>/claude-<user id>/<working folder, each slash made a hyphen>/<session id>/scratchpad`. Every hook is given
it as `scratchpad_dir` in its input. Scripts that Claude runs take it as `--scratchpad <path>`,
where `--data` is today. A script refuses a path that does not exist or does not end in
`/<session id>/scratchpad`, using the session id it is already given, and names the reason. With
no scratchpad, the file goes in `agentic-<user id>` in the system's temporary folder, made so only
that user can open it, as [ADR 0033](0033-end-of-run-report.md) does today.

**What moves.** Under `<scratchpad>/agentic/`: `reports/` (build, audit and verify reports, named
as [ADR 0033](0033-end-of-run-report.md) names them), `reviews/`, `builds/`, `audits/`,
`verifies/`, `sessions/` and the experiment step's working folders. This ADR supersedes only
[ADR 0033](0033-end-of-run-report.md): wherever [ADR 0034](0034-report-copied-by-script.md),
[ADR 0040](0040-verify-built-product-outside.md) and [ADR 0050](0050-checker-hook-answers.md)
name the plugin's data folder, the scratchpad replaces it, and their decisions stand.

**Evidence.** On Claude Code 2.1.328, three headless runs with a hook logging its input found
`scratchpad_dir` on every event the plugin uses (session start and end, prompt, before and after a
tool, including a reviewer agent's own tools, when an agent returns its result, when any agent
stops, and when the session stops), always the path
Claude itself was given. Resuming the session gave the same path, and a file left there was still
there. In one run, Claude mistyped the long path once, hence the check above.

[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed by separate Claude agents.
[^audit]: An audit is the plugin's step that checks whether the code still agrees with the project's accepted documents.
[^verify]: A verify run is the plugin's step that starts the built product and checks it against the accepted specs from outside.
[^scratchpad]: The scratchpad is a folder Claude Code gives each session for temporary files; Claude Code decides when it is cleared.
[^data]: The plugin's data folder is a folder Claude Code gives each plugin in the person's home folder, outside every repository, kept until the plugin is uninstalled.
[^thread]: A Claude project thread is one conversation inside a project in the Claude app; a file attached to a reply there is kept with the project.
