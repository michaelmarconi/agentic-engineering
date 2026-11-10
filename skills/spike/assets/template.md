---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spike
status: 📝 Draft
---

# <The hypothesis, in plain words>

<!-- The record reads from plain to technical. Everything above Experiment is for people: at most
     600 words, tables included, in plain words, with no versions, settings, file names or code
     names unless the hypothesis is about one of them. Those go in Experiment. -->

## Hypothesis

<!-- The one claim the experiment tests, in one to three sentences, and the spec or ADR waiting
     on it, if any. No method. -->

## Finding

<!-- Written after the runs: Confirmed, Refuted or Not settled, followed by what was found, in
     full, so it reads on its own. Then up to three sentences of evidence, by run number. -->

## Next steps

<!-- Written after the runs. -->
- Spec: <what should change in which spec, or "Nothing">
- ADR: <which choice an ADR should record, or "Nothing">

## How we'll know

<!-- The result that would confirm or refute the hypothesis, fixed before any run, such as "all
     20 sample files open" or "under 200 milliseconds for a million rows". -->

## Out of scope

<!-- Each limit of the finding, stated once here and nowhere else, or "None." -->

## How the test works

<!-- What the experiment does, as a numbered list or a table of steps, why that tests the
     hypothesis, and why it runs as many times as it does. -->

## Risks and safeguards

<!-- When the experiment changes or reads anything real, such as a live account, real data or
     money: each way it could do harm and what stops it. Otherwise "None." -->

## Results

<!-- Written after the runs: a table with a row for every run in Runs, then which runs count.
     | Run | Date | Outcome | Note |
     |---|---|---|---|
     | 1 | 2026-11-04 | Confirmed | All 12 transactions read. | -->

## Surprises

<!-- Written after the runs: anything unexpected they showed, including any limit they
     uncovered, since Out of scope is fixed by then; or "None." -->

## Open questions

<!-- What only the person can settle about the spike; "None." before it moves on. -->
- None.

## Experiment

<!-- From here down is for agents and reviewers. The full method, the exact rules for what counts
     as confirmed or refuted, and every safeguard in detail. Then these lines, exactly so, since
     the run script reads them. Values go in backticks; "None." when there are none. -->

- Runs: <how many times, as a number>
- Stop early if: <a result that ends the runs early, such as a crash showing the approach can't work, or "None.">
- Starts from commit: <`commit`, when it needs the product's own code or files, or "None.">
- Inputs: <`path/in/that/commit`, `https://web.address/file`, or "None.">
- Secrets: <`ENVIRONMENT_VARIABLE_NAME`, or "None.">
- Command: <`the command, with any install step`>

## Code

<!-- Each code block names its file on its first line, such as `# file: check.py`. A change to
     the product's own code is a `diff` block, applied to the commit above. -->

## Runs
