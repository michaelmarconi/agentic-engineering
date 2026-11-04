---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to run
---

# Does ledgerlint accept our statement layout?

## Question

Does the ledgerlint checking tool accept a statement in the bank's layout as valid?

## What would answer it

`ledgerlint --check sample.csv` exits with code 0 and prints `valid`.

## Experiment

Writes a two-line statement in the bank's layout and checks it with ledgerlint. A check of a file gives the same result every time, so one run is enough.

- Runs: 1
- Stop early if: None.
- Starts from commit: None.
- Inputs: None.
- Secrets: None.
- Command: `ledgerlint --check sample.csv`

## Answer

## Surprises

## Where it goes

## Open questions

- None.

## Code

```csv
# file: sample.csv
date;payee;amount
2026-10-01;Mill;-120,00
```

## Runs
