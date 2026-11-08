---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to run
---

# The till printer prints the euro sign

## Hypothesis

The till printer in the first bakery prints the euro sign on a receipt.

## Finding

## Next steps

## How we'll know

The test receipt shows `€ 1,00`, with the euro sign as drawn on the till's screen.

## Out of scope

- One till stands for every till in the bakeries.

## How the test works

1. The accounts clerk prints the till's test receipt.
2. They say what the amount line shows.

Only a person standing at the till can do this, so the run is their observation. One print is enough, since the printer prints the same character every time.

## Risks and safeguards

- The till is real: the test receipt is its own test print, so no sale is recorded.

## Results

## Surprises

## Open questions

- None.

## Experiment

The run is recorded through the run script as the clerk's observation, in their words. It holds when they report `€ 1,00` with the euro sign; any other character refutes it.

- Runs: 1
- Stop early if: None.
- Starts from commit: None.
- Inputs: None.
- Secrets: None.
- Command: None.

## Code

None: this experiment is a person's observation.

## Runs
