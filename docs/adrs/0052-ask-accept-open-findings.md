---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0052
status: Superseded ↪️
date: 2026-11-26
supersedes: 0038
superseded-by: 0060
---

# Ask at the end of a failing build whether to accept its open findings

## Question

When a build's[^build] correction check[^check] fails, when does the person[^person] get to accept
the build as it stands, so its plan[^plan] can still become `✅ Built`?

## Decision

Chosen: the build asks at its own end, right after the failed check and in the same session,
whether to accept the build as it stands or leave the plan `🟢 Ready to build`; on "accept", the
hand-over script[^handover] marks the plan `✅ Built` and lists the open findings[^finding] in that
commit. The answer comes in the same session, so no file has to outlast it;
[ADR 0051](0051-every-file-outside-scratchpad.md) keeps reports only in the session's scratchpad.

## Background

[ADR 0038](0038-accept-open-findings.md) let the person accept a failed build by running
`/build` again, which reads the last build's report to find the open findings. ADR 0051 now keeps
reports only in the session's scratchpad[^scratchpad], so a run in a new session finds none. The
need to stop a cycle of reviews and corrections that may never stop finding new problems is unchanged.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Run `/build` again, which reads the last report, as now | Rejected | The report no longer outlasts the session |
| Record the failed check in the hand-over commit, for the next run to read | Rejected | Adds a record to the branch only to be read back |
| Ask at the end of the failing build, in the same session | Chosen | Needs nothing kept after the session |
| Settle the findings and build again | Rejected | New reviews raise new findings each round |

## Consequences

- Good: accepting works the same in the terminal, the desktop app and a project thread[^thread].
- Good: the hand-over reads only a report this session wrote.
- Bad: once the scratchpad is cleared, the person can only build again, with fresh reviews.
- Bad: a plan can be `✅ Built` with known findings left open, and is then frozen.

## Out of scope

- A build that stopped before its correction check, such as on failing tests.
- A plan the person told Claude to build before approving it.
- Other documents, such as specs[^spec], which still need a passing review.

## How we'll check

Applies to: anything that marks a plan `✅ Built`, or asks the person whether to.

1. Test: after a failed correction check, a test build asks once and, on "accept", marks the plan Built, listing the open findings in its commit.
2. Test: on "leave it", or with no answer, nothing changes.
3. Test: the hand-over script refuses to accept when the branch changed since the check, the report is not in this session's scratchpad, or either case under Out of scope holds.
4. Test: `/build` run again on the branch starts a fresh review and offers no acceptance.
5. Inspection: the explanation and question match Technical detail.

## Open questions

None.

## Technical detail

**Finding the failed check.** The hand-over script reads the newest build report for the plan in
this session's scratchpad, by date and then by the number suffix (`-2`, `-3`) added when several share a date. `--open-findings` and
`--accept-open-findings` keep their meaning and every condition ADR 0038 lists: the plan is
`🟢 Ready to build`; the report's correction check says `Result: FAIL`; its `Head:` line matches the
branch's current commit, with nothing uncommitted; its `## Built before sign-off` section is empty.
It then sets the plan `✅ Built` and its `date:`, and commits it with a body that copies, word for
word, the check's `Corrections:` lines marked `not made` or `left for the person` and its
`Broken by a correction:` lines other than `None.`, under the line "Accepted as it stands by the
person, without further review:". It then pushes and writes a new report.

**When it is asked.** Once the hand-over after a failed check has written its report, `/build` runs
the script with `--open-findings`. When that prints open findings, it writes the plan's path, its
status, the open findings as a numbered list in plain words, the report's full path, and this
explanation, with the count filled in:

> If you accept the build as it stands, the plan is marked `✅ Built` with these 3 findings left
> open and no further review. The plan is then frozen and can never be built again, so any
> follow-up work needs a new plan. The commit that marks it `✅ Built` lists the 3 findings as
> accepted by you, so the pull request shows what you agreed to. If you leave it instead, the plan
> stays `🟢 Ready to build`: settle the open findings, then run `/build` again, which starts a fresh
> round of reviews.

It then asks, on Claude Code's question tool, "Accept the build as it stands, or leave it?", with
the options `✅ Built: accept as it stands` and `🟢 Ready to build: leave it`. `/build` at its start
no longer runs `--open-findings`.

[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed by three separate Claude agents.
[^check]: The correction check is the agent that, after the build corrects what the reviews found once, checks those corrections; it passes or fails.
[^person]: The person is whoever is working with Claude and the plugin on the project.
[^plan]: A plan is the plugin's document that sets out one piece of work; `✅ Built` marks it done and frozen.
[^handover]: The hand-over script is the program a build ends with: it commits the branch, sets the plan's status and pushes the branch.
[^finding]: An open finding is something a review raised that the correction check found not corrected, left for the person, or broken by a correction.
[^scratchpad]: The scratchpad is a folder Claude Code gives each session for temporary files; Claude Code decides when it is cleared.
[^thread]: A Claude project thread is one conversation inside a project in the Claude app, where each piece of work gets a thread of its own.
[^spec]: A spec is the plugin's document that says what one capability of a product should do.
