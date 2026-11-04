---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
---

# Can the importer read the bank's statement file as the bank sends it?

## Question

Can the importer in `src/importer.py`, as it stands, read the bank's monthly statement file without anyone converting it first? It comes from the open question in the statement import spec.

## What would answer it

The importer reads all 12 transactions in `samples/statement.csv`, a real statement with the account number removed, without an error, and prints each payee's name as the statement shows it.

## Experiment

Reads the sample statement with the importer's own `read_statement` function and prints every row. Reading a file gives the same result every time, so one run is enough.

- Runs: 1
- Stop early if: None.
- Starts from commit: `@COMMIT@`
- Inputs: `samples/statement.csv`
- Secrets: None.
- Command: `python3 check_statement.py`

## Answer

## Surprises

## Where it goes

## Open questions

- None.

## Code

```python
# file: check_statement.py
import sys

sys.path.insert(0, "src")
from importer import read_statement

rows = read_statement("samples/statement.csv")
print(len(rows), "transactions read")
for row in rows:
    print(row)
```

## Runs
