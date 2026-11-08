---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to run
---

# The importer reads the bank's file when it reads it as Latin-1

## Hypothesis

The importer reads every transaction in the bank's statement file when it opens the file as Latin-1 instead of UTF-8. Latin-1 and UTF-8 are two ways of storing letters as bytes.

## Finding

## Next steps

## How we'll know

The importer reads all 12 transactions in the sample statement without an error, and prints each payee's name as the statement shows it.

## Out of scope

- One month's statement stands for every statement the bank sends.

## How the test works

1. Change the importer to open the file as Latin-1, on a copy of the code.
2. Read a real statement, with the account number removed, with the changed importer.
3. Print how many transactions it read, and each one.

Reading a file gives the same result every time, so one run is enough.

## Risks and safeguards

- The sample is a real statement. Its account number was removed before it was added, and the experiment only reads it, on this machine.

## Results

## Surprises

## Open questions

- None.

## Experiment

Applies the diff below to `src/importer.py` at the commit below, then reads `samples/statement.csv` with `read_statement`. It holds when the script prints `12 transactions read` and every payee's name as written, such as `Café Lune`; an error, or fewer rows, refutes it.

- Runs: 1
- Stop early if: None.
- Starts from commit: `@COMMIT@`
- Inputs: `samples/statement.csv`
- Secrets: None.
- Command: `python3 check_statement.py`

## Code

```diff
--- a/src/importer.py
+++ b/src/importer.py
@@ -5,5 +5,5 @@ import csv
 
 def read_statement(path):
     """Return the statement's transactions as lists of [date, payee, amount], header left out."""
-    with open(path, newline="", encoding="utf-8") as f:
+    with open(path, newline="", encoding="latin-1") as f:
         return [row for row in csv.reader(f, delimiter=";")][1:]
```

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
