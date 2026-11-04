---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to run
---

# Does Python's csv module keep a quoted field holding a line break as one field?

## Question

Does Python's standard `csv` module read a quoted field that holds a line break as one field, so a payee's note written over two lines stays in one row?

## What would answer it

The script prints `1 row(s), 3 fields` on every run.

## Experiment

Reads a one-line sample, held in the code, whose middle field is quoted and holds a line break, and prints how many rows and fields it found. The team asked for three runs, one for each bakery's laptop it will be checked on later, so it runs three times.

- Runs: 3
- Stop early if: None.
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

rows = list(csv.reader(io.StringIO('2026-10-01,"line one\nline two",-12.40\n')))
print(len(rows), "row(s),", len(rows[0]), "fields")
```

## Runs

### Run 1

2026-11-04 15:12 UTC, Linux 6.18.44-fc-v233, your machine, code `c8c9e21d5a57`, exit code 0

```
1 row(s), 3 fields
```
