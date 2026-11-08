---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
---

# The importer reads the bank's statement file as the bank sends it

## Hypothesis

The importer, as it stands, reads the bank's monthly statement file without anyone converting it first. The statement import spec waits on this, in its open questions.

## Finding

## Next steps

## How we'll know

The importer is fast enough on the statement and reads it fine.

## Out of scope

- One month's statement stands for every statement the bank sends.

## How the test works

1. Read a real statement, with the account number removed, using the importer's own code as it stands.
2. Print how many transactions it read, and each one.

Reading a file gives the same result every time, so one run is enough.

## Risks and safeguards

- The sample is a real statement. Its account number was removed before it was added, and the experiment only reads it, on this machine.

## Results

## Surprises

## Open questions

- None.

## Experiment

Imports `read_statement` from `src/importer.py` at the commit below, reads the sample statement and prints every row.

- Runs: 1
- Stop early if: None.
- Starts from commit: `@COMMIT@`
- Inputs: None.
- Secrets: None.
- Command: `python3 check_statement.py`

## Code

<!-- Each code block names its file on its first line. -->

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
