---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-16
---

# Let the person accept the open findings of a build and mark its plan Built

## Question

When a build's[^build] correction check[^check] fails, how can its plan[^plan] still become
`✅ Built` without another round of reviews?

## Decision

Chosen: `/build`, run again on a branch, first checks whether its last correction check failed
with nothing changed since. If so, it explains what is still open and asks the person[^person] once
whether to accept the build as it stands or correct it; on "accept", the hand-over
script[^handover] marks the plan `✅ Built` and lists the open findings[^finding] in that commit.
This ends a review loop that need not converge, and the pull request records what was accepted.

## Background

Today a plan becomes `✅ Built` only when every review, or the one correction check after them,
passes ([ADR 0010](0010-correction-check.md)). When the check fails, the only way on is
to settle every finding and build again, with three fresh reviews. Fresh reviewers
raise new findings, so the loop need not end. So the person merges the work instead,
leaving the plan `🟢 Ready to build` and no record of what was accepted.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Settle the findings and build again, as now | Rejected | Fresh reviews raise new findings each round |
| The person sets the status by hand | Rejected | Nothing checks it or records what was accepted |
| Ask once whether to accept the build as it stands, recording the findings in the Built commit | Chosen | One decision ends the loop; the record travels with the pull request |
| Accept or reject each finding, with a reason for each | Rejected | More questions add no safety |
| Record the acceptance only in the build's report[^report] | Rejected | The report stays on one computer, outside the repository |

## Consequences

- Good: a person can end a build the reviews never let finish.
- Good: the plan's status matches the merged work.
- Bad: a plan can be `✅ Built` with known findings left open.
- Bad: the plan is then frozen, so follow-up work needs a new plan.
- Bad: a build whose report is on another computer is reviewed again.

## Out of scope

- A build changed since its correction check.
- A build that stopped before its correction check, such as on failing tests.
- A plan the person told Claude to build before approving it.
- Other documents, such as specs, which still need a passing review.

## How we'll check

Applies to: anything that marks a plan `✅ Built`, or asks the person whether to.

1. Test: the hand-over script marks the plan Built, listing the open findings in its commit.
2. Test: the script refuses in the first three cases under Out of scope, with no report, or with the plan not `🟢 Ready to build`.
3. Test: a test build on a branch whose newest report records a failed correction check asks once, starts no review and marks the plan Built.
4. Test: when the script gives a reason instead, the build asks nothing and reviews again.
5. Inspection: the explanation and question match Technical detail.

## Open questions

None.

## Technical detail

**Finding the failed check.** The hand-over script writes each build's report file
([ADR 0033](0033-end-of-run-report.md), [ADR 0034](0034-report-copied-by-script.md)). It gains a
line in its own report naming the commit the branch was at, `Head: <full commit id>`. The report
that counts is the newest build report for the plan, by date and then by the number suffix (`-2`, `-3`) added to the file name when several reports
share a date,
whatever run wrote it: a later run that stopped early or passed has no failed check, so it hides an
earlier failure. The script looks in the plugin's data folder, `${CLAUDE_PLUGIN_DATA}/reports/<repository>/`,
and, when nothing is found there, in the private folder inside the system's temporary folder that
[ADR 0033](0033-end-of-run-report.md) falls back to. Two new options use that report.
`--open-findings` prints the open findings and the report's full path, or the reason none can be
accepted, and changes nothing. `--accept-open-findings` goes ahead only when all of the following
hold, and refuses with the reason otherwise, changing nothing:

- the plan is `🟢 Ready to build`;
- the report's correction check says `Result: FAIL`; that report lists each correction under
  `Corrections:` as `- <finding>: made | not made | left for the person`, and anything a
  correction broke under `Broken by a correction:`;
- the report's `Head:` line matches the branch's current commit, and nothing is uncommitted;
- the report's `## Built before sign-off` section, which the build skill fills when the person had
  it build a plan they had not yet approved, is empty.

It then sets the plan `✅ Built` and its `date:`, as the script already does when every review passes, and commits it with a
body that copies, word for word, the check's `Corrections:` lines marked `not made` or `left for
the person` and its `Broken by a correction:` lines other than `None.`, under the line "Accepted as
it stands by the person, without further review:". It then pushes and writes a new report.

**What the person sees.** `/build` on a branch that already holds work first runs the script with
`--open-findings`. When that prints open findings, it starts no review, and writes the plan's
path, its status, the open findings as a numbered list in plain words, the report's full path, and
this explanation, with the count filled in:

> If you accept the build as it stands, the plan is marked `✅ Built` with these 3 findings left
> open and no further review. The plan is then frozen and can never be built again, so any
> follow-up work needs a new plan. The commit that marks it `✅ Built` lists the 3 findings as
> accepted by you, so the pull request shows what you agreed to. If you correct it instead, the plan
> stays `🟢 Ready to build`: settle the open findings, making the choice or having Claude change the
> code, then run `/build` again, which starts a fresh round of reviews.

It then asks, on Claude Code's question tool, "Accept the build as it stands, or correct it?",
with the options `✅ Built: accept as it stands` and `🟢 Ready to build: correct it`. On "correct it", or with no answer, nothing changes. When the
script prints a reason instead, `/build` resumes as before, reviewing again.

[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed by three separate Claude agents.
[^check]: The correction check is the agent that, after the build corrects what the reviews found once, checks those corrections; it passes or fails.
[^plan]: A plan is the plugin's document that sets out one piece of work; `✅ Built` marks it done and frozen.
[^person]: The person is whoever is working with Claude and the plugin on the project.
[^handover]: The hand-over script is the program a build ends with: it commits the branch, sets the plan's status and pushes the branch.
[^report]: The build's report is a file the hand-over script writes on the person's own computer, outside the repository, recording how the build went.
[^finding]: An open finding is something a review raised that the correction check found not corrected, left for the person, or broken by a correction.
