---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to run
---

# Does the importer read the bank's file when it reads it as Latin-1?

## Question

Does the importer read every transaction in the bank's statement file when it opens the file as Latin-1 instead of UTF-8?

## What would answer it

The importer reads all 12 transactions in `samples/statement.csv`, a real statement with the account number removed, without an error, and prints each payee's name as the statement shows it.

## Experiment

Changes the importer to open the file as Latin-1, then reads the sample statement with it and prints every row. Reading a file gives the same result every time, so one run is enough.

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
