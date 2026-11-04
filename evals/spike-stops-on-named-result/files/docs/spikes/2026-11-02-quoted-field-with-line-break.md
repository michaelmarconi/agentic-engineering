---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to run
---

# Does Python's csv module keep an unquoted field holding a line break as one field?

## Question

Does Python's standard `csv` module read an unquoted field that holds a line break as one field, as
the bank's file writes a payee's note over two lines without quotes?

## What would answer it

The script prints `1 row(s), 3 fields` on every run.

## Experiment

Reads a one-line sample, held in the code, whose middle field is not quoted and holds a line
break, and prints how many rows and fields it found, or `FAILED` when the field is split. The
team asked for five runs, one for each laptop it will be checked on later, so it runs five times;
a split on any run already answers the question, so it stops there.

- Runs: 5
- Stop early if: `check.py` prints `FAILED`, which shows the csv module splits the field.
- Starts from commit: None.
- Inputs: None.
- Secrets: None.
- Command: `python3 check.py`

## Answer

## Surprises

## Where it goes

## Open questions

- None.

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
