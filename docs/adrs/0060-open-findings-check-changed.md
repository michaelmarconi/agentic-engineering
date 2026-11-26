---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0060
status: Accepted 👍
date: 2026-11-26
supersedes: 0052
---

# Go through a build's open findings with the person and check only what changed

## Question

When a build's[^build] correction check[^check] leaves findings[^finding] open, how does the
person[^person] settle them and still get the plan[^plan] to `Built ✅`?

## Decision

Chosen: the build puts each of its own open findings to the person one at a time, with a proposal,
to accept, answer, ignore or defer to a later plan, and makes the fixes chosen on the same branch.
The correction checker then looks at only the commits since its last check, with the answers.
Findings in older code are first summed up by count and severity, to go through or carry on past.
The last question offers `Built ✅`, marked by the hand-over script[^handover] at the commit last
checked, one more full review, or stopping. A full review runs only when the person asks.

## Background

[ADR 0052](0052-ask-accept-open-findings.md) asks once, right after a failed check, whether to
accept the build as it stands, and refuses once the branch has changed. A person who settles even
one finding with a fix can then only run all three reviews again. Those read whole files, so they
report new problems, or the same ones, and fail again.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Go through each finding, fix on the branch, check only what changed | Chosen | Ends as `/spec` and `/adr` do, and each fix is still checked |
| Ask once whether to accept as it stands, as now | Rejected | Any fix forces all three reviews again, which may never pass |
| Accept any branch state without a further check | Rejected | Fixes made while going through findings would go unchecked |

## Consequences

- Good: the build ends with the person's answers, as `/spec` and `/adr` do.
- Good: every fix is checked before the plan is marked `Built ✅`.
- Bad: a plan can be `Built ✅` with findings the person ignored or deferred, and is then never edited again.
- Bad: the plugin hook that passes the reports to the correction checker must also keep the commit last checked and the answers.

## Out of scope

- Which findings count as in older code, which [ADR 0061](0061-checker-sorts-findings.md) decides.
- A build that stopped before its reviews, such as on failing tests.
- A plan the person chose to build before approving it, which keeps its status as now.
- A new conversation, where `/build` reviews afresh.

## How we'll check

Applies to: anything that marks a plan `Built ✅` after a failed correction check, or asks the person about open findings.

1. Test: the plugin hook starts a second correction check after new commits, attaching the commit last checked and the answers.
2. Test: the hand-over script accepts at the commit of the newest check, whatever its result, and refuses a branch changed since then.
3. Test: the commit that marks the plan `Built ✅` lists each finding left open, with the person's choice.
4. Demonstration: an automated test run of `/build` puts each open finding to the person one at a time and runs no full review for the answers.

## Open questions

None.

## Technical detail

**Asking.** After the hand-over that follows a failed check, `/build` runs the hand-over script
with `--open-findings` and asks about each finding it prints, one question at a time, numbered,
each with a proposal such as fixing it or dropping a test the code cannot meet, and each ending
"Accept, give your own answer, ignore or defer?". Accept and My own answer make the fix on the
branch and commit it; Ignore leaves the finding as it is; Defer leaves it for a later plan.
Findings the check lists under `Outside this build:` are not asked one by one: `/build` gives
their count by grade, such as "1 high, 2 medium, 1 low", and asks "go through them, or carry
on?". The checker grades each: high is wrong results, a crash, lost data or a security hole;
medium is wrong behaviour in edge cases; low is anything else.

**Checking what changed.** The build relay hook (`scripts/build_relay.py`) keeps, beside the three
reports, the commit each correction check ran at and the person's answers since then, captured as
`scripts/review_relay.py` captures them for documents. When the checker starts again, the hook
attaches the commit last checked between `=== LAST CHECKED COMMIT ===` lines and the answers
between `=== ANSWERS ===` lines, and the checker reads `git diff <last checked>..HEAD`. The changed
lines [ADR 0061](0061-checker-sorts-findings.md) attaches run from the merge base to the commit now being checked. The hook refuses
when nothing was committed since the last check.

**Accepting.** `--accept-open-findings` keeps every condition of
[ADR 0052](0052-ask-accept-open-findings.md) (the plan is `Ready to build 🟢`, it was not built
before approval, the report is this session's) except one: the report's `Head:` line, the commit
the check ran at, must now match the commit of the newest correction check, which may have passed
or failed, and nothing may be uncommitted. The commit body lists, under "Left open by the person,
without further review:", each finding still open with Ignore or Defer, and each outside finding
the person carried on past.

[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed by three separate agents, each reading whole files.
[^check]: The correction check is the agent that checks the corrections a build made after its reviews; it passes or fails.
[^finding]: A finding is a problem a review raised; it is open when the correction check found it not corrected, left for the person, or broken by a correction.
[^person]: The person is whoever is working with the agent and the plugin on the project.
[^plan]: A plan is the plugin's document that sets out one piece of work; `Built ✅` marks it done, after which it is never edited again.
[^handover]: The hand-over script is the program a build ends with: it commits the branch, sets the plan's status and pushes the branch.
