---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: Spike
status: 📝 Draft
date: 2026-11-02
---

# The importer reads the bank's statement file as the bank sends it

## Hypothesis

The importer reads every transaction in the bank's monthly statement file exactly as the bank sends it, with no one converting or cleaning the file before the importer opens it. The statement import spec waits on this, in its open questions.

## Finding

## Next steps

## How we'll know

Confirmed if the importer reads all 12 transactions in the sample, each with the date, payee and amount the bank's website lists for it. Refuted if any transaction is missing or differs.

## Out of scope

- One month's statement stands for every statement the bank sends.

## How the test works

1. Read a real statement, with the account number removed, using the importer's own code as it stands.
2. Print how many transactions it read, and each one.

Reading a file gives the same result every time, so one run is enough. The sample is last month's statement, with the account number removed. It holds 12 transactions, which the bank's website also lists. So the printed transactions can be compared with that list by eye.

## Risks and safeguards

- The sample is a real statement. Its account number was removed before it was added, and the experiment only reads it, on this machine.
- The sample is not a statement that is not real, so it is not read anywhere it is not safe not to.

## Results

## Surprises

## Open questions

- None.

## Experiment

Imports `read_statement` from `src/importer.py` at the commit below, reads the sample statement and prints every row.

- Runs: 1
- Stop early if: None.
- Starts from commit: `@COMMIT@`
- Inputs: `samples/statement.csv`, last month's statement with the account number removed.
- Secrets: None.
- Command: `python3 check_statement.py`

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
