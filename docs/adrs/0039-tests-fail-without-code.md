---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: 2026-11-16
---

# Check that each requirement's tests fail without its code before committing them

## Question

How does the plugin make sure a build[^build] writes each requirement's[^requirement] tests, and
sees them fail, before it writes that requirement's code?

## Decision

Chosen: before writing a requirement's code, the build runs a script that refuses that
requirement's tests if any new or changed test file passes or any other file is uncommitted; the
build checks each failure comes from the missing code, then commits the tests, reports the result,
and is reminded of this rule at each commit. This stops code being written before its tests, at 1.25
times today's cost in one trial.

## Background

The plugin's build step tells Claude to see each requirement's tests fail before writing its code.
In one build, Claude wrote two of twelve requirements' code first. The reviewer[^reviewer] judged the
same commit order differently in two review rounds. The early code was found after the push,
when fixing it meant rewriting commits.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Check each requirement's tests fail before its code, with a commit reminder | Chosen | Refuses early code, at 1.25 times today's cost |
| Run new tests on the code from before the build, once at the end | Rejected | Tests of code in new files always fail there, so the run proves nothing |
| A separate agent writes every test, and the build writes the code | Rejected | 1.6 times the cost in a trial |
| Separate agents write tests and code, plus one passing work | Rejected | 3 times the cost and nearly 3 times the time, in trials |
| Label commits by requirement, then check their order | Rejected | Adds records to the person's commits |
| Only reword the instructions and the reviewer's check | Rejected | Already clear, yet not followed |

## Consequences

- Good: the reviewer reads recorded results instead of judging the commit order.
- Bad: one more test run per requirement, and a line of context per commit.
- Bad: a file that cannot load also fails, so the build must read why.

## Out of scope

- Whether the tests check what the examples in the spec[^spec] say: the reviewer's tests check covers that.
- Judging tests one by one: the script judges whole files.
- Code committed before the build started, by a build that stopped: its tests are refused,
  committed anyway, and reported as built before its tests.

## How we'll check

Applies to: any build step that commits a requirement's tests.

1. Test: unit tests run the script where a named file fails, passes or is unchanged, or other files are uncommitted.
2. Test: unit tests check the reminder is added to commits only during a build.
3. Inspection: the build runs the script before committing each requirement's tests, and reports every result.
4. Inspection: the reviewer's tests-first check reads those results, not the commit order.

## Open questions

### 1. Whether the reminder at each commit belongs in this decision

The reminder could be replaced on its own.

> **Proposed:** Keep it in this decision.
>
> **Why:** It was tested only together with the check, as one option.

## Technical detail

**The script.** `skills/build/scripts/tests_fail.py --command "<command with {file}>" FILE...`,
run from the repository. It lists the uncommitted paths and refuses, exit 1, when a named file is
not new or changed, when anything other than the named files is uncommitted ("code must wait until
its tests are committed"), or when any named file's command exits 0 ("its tests already pass, so
they cannot show the code works"). Otherwise it prints "Red: every new test file fails." and exits
0. Exit 2 is a usage error, or a folder outside a git work tree. It prints the last lines of each
file's output. A changed file keeps its older tests, which pass, so it fails only when a test the
build added fails.

**The build.** For each requirement, the build writes its tests, runs the script with the command
that runs one test file (from the project's recorded working rules, or worked out from the repository), and reads each
failure: it must come from the missing behaviour, not from a file that cannot load. On exit 0 it
commits the tests, then writes the code. On exit 1 it corrects what the script names and runs it
again. The report's "Tests and lint" section gives each requirement's result.

**The reminder.** The build's existing Bash hook, during a build, adds this to every `git commit`
as `additionalContext`, worded as a fact, as Claude Code's hook guidance advises: "Build rule: a
requirement's tests are committed on their own, once tests_fail.py accepts them, and before any of
its code is written; its code is committed after."

**The reviewer.** The tests-first check passes when the report gives an accepted result for each
requirement with tests, or a refusal with a reason the reviewer accepts.

**Evidence.** On a small project made for the trial, not the twelve-requirement build above: eight
requirements, with code for two committed before their tests by an earlier stopped build. "Refused"
means the script turned those two requirements' tests away; today's build has no script, so did
not check. This option's ratio of 1.25 rests on one run.

| Build | Cost | Time | Early code refused |
| --- | --- | --- | --- |
| Today's build (2 runs) | $1.69 average | 4.0 minutes | not checked |
| This option (1 run) | $2.12 | 3.7 minutes | yes |
| Separate test-writer agent (1 run) | $2.74 | 5.8 minutes | yes |
| Three agents (2 runs) | $5.11 average | 11.5 minutes | yes |

In this option's run the script ran for all eight requirements, always before their code, and the
reminder appeared at every commit. One test file had a syntax error, so it failed and was accepted;
the build found it, corrected it after writing the code and reported it.

[^build]: A build is the plugin's step that writes the code for one plan, tests first, on a branch of its own, and has it reviewed by separate Claude agents.
[^requirement]: A requirement is one numbered rule in a spec, with examples a test can check.
[^reviewer]: The reviewer is the separate Claude agent that checks a build against its plan before it is handed over.
[^spec]: A spec is the plugin's document saying what one capability of the product should do.
