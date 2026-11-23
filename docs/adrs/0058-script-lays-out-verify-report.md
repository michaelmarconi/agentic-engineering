---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0058
status: Draft 📝
date: 2026-11-23
---

# Script lays out the verify report from each agent's fixed-shape entries

## Question

Who lays out the report a verify run[^verify] ends with, so a person can take in the results from
the top and still find the evidence for each example[^example] below?

## Decision

Chosen: the verify script lays out the report from the two verify agents' reports, which give one
entry per example in a fixed shape, and refuses an agent report that breaks that shape; the agent
that runs the verify step writes only what needs doing and any caveats. A script gives the same table,
counts and arrangement of details on every run, and puts each agent's words in unchanged.

## Background

Today the agent that runs the verify step writes the result sections, and the script pastes each agent's
report below them as one block, word for word, as
[ADR 0034](0034-report-copied-by-script.md) decided. The resulting report is hard to scan: the same
facts appear three times, one example's evidence is split between two agents' blocks, and long
commands fill most of the page. A person wants one results table at the top, then each example's
evidence from both agents together.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| The script lays out the report from the agents' fixed-shape entries | Chosen | Same layout every run, and the agents' words go in unchanged |
| The agent writes the table and each example's details, and the script only checks the shape | Rejected | Counts could slip, and a long report may be reworded when the agent copies it into the report |
| Keep the layout as it is | Rejected | The report stays hard to scan |

## Consequences

- Good: every report has one results table, with counts the script works out, not the agent.
- Good: each example's evidence from both agents sits together under that example.
- Bad: the agents must keep to a strict report shape, and a report that breaks it stops the run's
  report until it is corrected.

## Out of scope

- How the report links to the spec, which [ADR 0059](0059-link-verify-report-github.md) decides.
- Where the report file goes and how it is shown, which [ADR 0051](0051-every-file-outside-scratchpad.md) decides.
- The reports of the plugin's build and audit steps, which keep their layout.
- Sections with nothing in them, which still say "Nothing to report".

## How we'll check

Applies to: the verify script's report step and the shape of the verify agents' reports.

1. Test: unit tests give the script sample agent reports and check the table, counts, details and commands section it writes.
2. Test: unit tests check each agent's words reach the file unchanged.
3. Test: unit tests check the script refuses an agent report that breaks the shape, saying where.
4. Demonstration: an eval runs the skill on a stand-in project and reads the report it writes.

## Open questions

None.

## Technical detail

**Agent report shape.** `agents/verifier.md` and `agents/verify-checker.md` report:

```
Document: <path>
Started: <the start command, and whether the product started>    (verifier only)

<requirement number>. <requirement name>
- <example name>: <verdict>
  - Did: <what was run, as run>
  - Saw: <what came back, quoted exactly, cut to what decides it>
  - Why: <fail, not checked or rejected only>

Commands:
- <every command, in order, exactly as run>
```

The verifier's verdict is `pass`, `fail` or `not checked`; the checker's is `confirmed` or
`rejected`. `Saw` replaces the earlier `Got`. An agent that checked nothing still reports only its `Document:`
line and an `Error:` line with the reason.

**What the script writes.** `verify.py report` reads the reports the verify hook kept, and writes,
in order:

1. a title naming the spec and the requirements checked;
2. a header: the spec, the commit checked and the verifier's `Started:` line;
3. `## Result`: one bold line with the counts of passed, failed, disputed and not checked
   examples, and whether the checker agreed with every verdict; then one table with the columns
   `#` (right-aligned requirement number), `Requirement`, `Example` and `Result`, one row per
   example, the result one of ✅ Pass, ❌ Fail, ⚠️ Disputed or ⚠️ Not checked;
4. `## What needs doing` and `## Caveats`, the agent's own sections, given on standard input;
5. `## Details`: per example a `### <n>. <example name> — <result>` heading, then `**Verifier**`
   and `**Checker** (confirmed or rejected)`, each with its `Did` and `Saw` bullets;
6. `## The repository after the run`, written by the script: whether the commit checked is still
   checked out, and every file that changed in the repository during the run;
7. `## Commands`: one collapsed `<details>` block per agent holding its command list.

A disputed result is a verdict the checker rejected. A spec whose verifier reported `Error:` gives
each requested requirement one row, not checked. The script refuses, with the agent and line, an
entry it cannot read, an example in one agent's report but not the other's, and a verdict word it
does not know. Every sentence an agent wrote reaches the file unchanged, only placed under its
example.

[^verify]: A verify run is the plugin's step that starts the product and uses it from outside, as a person would, to check it against its specs, with one agent giving each example a verdict and a second agent trying to disprove it.
[^example]: In a spec, a requirement is one numbered rule the product must follow, and an example is one case under it, with a starting state, an action and the expected result, that can be tried on the product.
