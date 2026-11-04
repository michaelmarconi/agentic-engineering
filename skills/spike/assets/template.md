---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
---

# <The question, in plain words>

## Question

<!-- The one question, and the spec or ADR whose open question it is, if any. -->

## What would answer it

<!-- The result that settles the question, fixed before any run, such as "all 20 sample files
     open" or "under 200 milliseconds for a million rows". -->

## Experiment

<!-- What the experiment does and why that answers the question, and why it runs as many times
     as it does. Then these lines, exactly so, since the run script reads them. Values go in
     backticks; "None." when there are none. -->

- Runs: <how many times, as a number>
- Stop early if: <a result that ends the runs early, such as a crash showing the approach can't work, or "None.">
- Starts from commit: <`commit`, when it needs the product's own code or files, or "None.">
- Inputs: <`path/in/that/commit`, `https://web.address/file`, or "None.">
- Secrets: <`ENVIRONMENT_VARIABLE_NAME`, or "None.">
- Command: <`the command, with any install step`>

## Answer

<!-- Written after the runs: Yes, No, or Yes provided that <condition>, comparing the runs of
     the latest code with What would answer it. If the runs settled nothing, what was learned and
     what is still unknown. -->

## Surprises

<!-- Written after the runs: anything unexpected they showed, or "None." -->

## Where it goes

<!-- Written after the runs. -->
- Spec: <what should change in which spec, or "Nothing">
- ADR: <which choice an ADR should record, or "Nothing">

## Open questions

<!-- What only the person can settle about the spike; "None." before it moves on. -->
- None.

## Code

<!-- Each code block names its file on its first line, such as `# file: check.py`. A change to
     the product's own code is a `diff` block, applied to the commit above. -->

## Runs
