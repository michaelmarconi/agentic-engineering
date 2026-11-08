---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to run
---

# Python's csv module keeps an unquoted field holding a line break as one field

## Hypothesis

Python's standard csv module reads an unquoted field that holds a line break as one field, as the bank's file writes a payee's note over two lines without quotes.

## Finding

## Next steps

## How we'll know

The script prints `1 row(s), 3 fields` on every run.

## Out of scope

None.

## How the test works

1. Read a short sample, held in the code, whose middle field is not quoted and holds a line break.
2. Print how many rows and fields it found, or that the field was split.

The team asked for five runs, one for each laptop it will be checked on later. A split on any run already refutes the hypothesis, so the runs stop there.

## Risks and safeguards

None.

## Results

## Surprises

## Open questions

- None.

## Experiment

Parses the sample in `check.py` with `csv.reader` and prints the row and field counts, or `FAILED` when the field is split. It holds when every run prints `1 row(s), 3 fields`.

- Runs: 5
- Stop early if: `check.py` prints `FAILED`, which shows the csv module splits the field.
- Starts from commit: None.
- Inputs: None.
- Secrets: None.
- Command: `python3 check.py`

## Code

```python
# file: check.py
import csv
import io

rows = list(csv.reader(io.StringIO("2026-10-01,line one\nline two,-12.40\n")))
if len(rows) != 1:
    print("FAILED: the field was split into", len(rows), "rows")
else:
    print(len(rows), "row(s),", len(rows[0]), "fields")
```

## Runs
