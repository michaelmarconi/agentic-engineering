---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spike
status: 🟢 Ready to run
---

# Python's csv module keeps a quoted field holding a line break as one field

## Hypothesis

Python's standard csv module reads a quoted field that holds a line break as one field, so a payee's note written over two lines stays in one row.

## Finding

## Next steps

## How we'll know

The script prints `1 row(s), 3 fields` on every run.

## Out of scope

None.

## How the test works

1. Read a one-line sample, held in the code, whose middle field is quoted and holds a line break.
2. Print how many rows and fields it found.

Reading a fixed string gives the same result every time, so one run is enough.

## Risks and safeguards

None.

## Results

## Surprises

## Open questions

- None.

## Experiment

Parses the sample in `check.py` with `csv.reader` and prints the row and field counts. It holds when every run prints `1 row(s), 3 fields`; any other count refutes it.

- Runs: 1
- Stop early if: None.
- Starts from commit: None.
- Inputs: None.
- Secrets: None.
- Command: `python3 check.py`

## Code

```python
# file: check.py
import csv
import io

rows = list(csv.reader(io.StringIO('2026-10-01,"line one\nline two",-12.40\n')))
print(len(rows), "row(s),", len(rows[0]), "fields")
```

## Runs
