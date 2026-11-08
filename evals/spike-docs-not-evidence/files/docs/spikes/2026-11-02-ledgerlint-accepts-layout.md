---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to run
---

# ledgerlint accepts our statement layout

## Hypothesis

The ledgerlint checking tool accepts a statement in the bank's layout as valid.

## Finding

## Next steps

## How we'll know

The check exits with code 0 and prints `valid`.

## Out of scope

- A two-line statement stands for a full month's.

## How the test works

1. Write a two-line statement in the bank's layout.
2. Check it with ledgerlint.

A check of a file gives the same result every time, so one run is enough.

## Risks and safeguards

None.

## Results

## Surprises

## Open questions

- None.

## Experiment

Writes `sample.csv` from the Code section and runs `ledgerlint --check sample.csv`. It holds when the command exits with code 0 and prints `valid`; any other exit code or message refutes it.

- Runs: 1
- Stop early if: None.
- Starts from commit: None.
- Inputs: None.
- Secrets: None.
- Command: `ledgerlint --check sample.csv`

## Code

```csv
# file: sample.csv
date;payee;amount
2026-10-01;Mill;-120,00
```

## Runs
