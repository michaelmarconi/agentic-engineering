---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0061
status: Accepted 👍
date: 2026-11-26
---

# The correction checker sorts out findings in code the build did not change

## Question

How does a build[^build] tell a finding[^finding] in code it changed from one in older code it
never touched, so the older one does not fail the build?

## Decision

Chosen: a plugin hook gives the build's correction checker[^check] the lines the build changed,
file by file, and the checker lists each finding whose place falls outside those lines under
"Outside this build". A finding listed there never makes the check fail. The hook works out the
changed lines exactly; the checker only decides where each finding sits, since review reports
give a finding's place in no fixed shape.

## Background

The code review reads every file the build touched in full, so it also reports problems in parts
of those files the build never changed. Today each counts as not corrected, and the check fails on
work an earlier build did. Telling the two apart by file is not enough: a build that adds one line
to a file would own every problem in it.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| The hook gives the changed lines; the checker sorts the findings | Chosen | Exact lines, with judgement only where the reports vary |
| A script matches each finding's file and line against the changed lines | Rejected | Review reports give places in no reliable format |
| Give the checker the commits and let it read the changes itself | Rejected | Working out line numbers from changes is where a model slips |
| Count every finding as the build's own, as now | Rejected | Older code keeps failing builds |

## Consequences

- Good: a build fails only on problems in what it changed.
- Good: the person sees at once which problems come from earlier work.
- Bad: a finding in changed code that the checker wrongly puts outside would not fail the build.

## Out of scope

- What the person is asked about these findings, and how they are graded, which [ADR 0060](0060-open-findings-check-changed.md) decides.
- Findings the security review or the build review raise, which the checker sorts the same way.

## How we'll check

Applies to: the build correction checker's request and report.

1. Test: the plugin hook attaches the lines changed between the default branch and the commit being checked, file by file.
2. Test: the hand-over script[^handover] treats findings under "Outside this build" as apart from the build's own open findings.
3. Demonstration: an automated test run, with a fake code review reporting a problem in an untouched part of a changed file, shows it outside this build.

## Open questions

None.

## Technical detail

**Changed lines.** The build relay hook (`scripts/build_relay.py`) runs
`git diff -U0 <merge base with the default branch>..<commit being checked>` and turns each hunk's
`+start,count` into ranges of that version, one line per file, such as `src/parser.ts: 40-52, 88`,
or `src/lookup.ts: all (new file)`, between `=== CHANGED LINES ===` and `=== END CHANGED LINES ===`.
A file the build deleted is left out.

**Report.** The checker's report gains a section after `Broken by a correction:`:

```
Outside this build:
- <the finding, quoted briefly>: high | medium | low, with the file and line
```

The grade is the one [ADR 0060](0060-open-findings-check-changed.md) defines. A finding listed
there is not counted when the checker asks whether each correction was made, so
it never makes the result FAIL.

[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed by three separate agents.
[^finding]: A finding is a problem a review raised.
[^check]: The correction checker is the agent that checks the corrections a build made after its reviews; it passes or fails.
[^handover]: The hand-over script is the program a build ends with: it commits the branch, sets the plan's status and pushes the branch.
