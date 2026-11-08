---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 💡 Confirmed
---

# The importer reads the bank's file when it reads it as Latin-1

## Hypothesis

The importer reads every transaction in the bank's statement file when it opens the file as Latin-1 instead of UTF-8. Latin-1 and UTF-8 are two ways of storing letters as bytes.

## Finding

Confirmed: the importer reads every transaction in the bank's statement file when it opens the file as Latin-1. Run 1 read all 12 of 12 transactions, each payee's name as the statement shows it.

## Next steps

- Spec: Nothing
- ADR: reading the bank's file as Latin-1 is a choice, for an ADR.

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

| Run | Date | Outcome | Note |
|---|---|---|---|
| 1 | 2026-11-04 | Confirmed | All 12 transactions read, names as written. |

Run 1 counts.

## Surprises

None.

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

### Run 1

2026-11-04 15:12 UTC, Linux 6.18.44-fc-v233, your machine, code `b9342ab3845d`, exit code 0

```
12 transactions read
['2026-10-01', 'Café Lune', '-7,01']
['2026-10-02', 'Moulin Blé', '-14,02']
['2026-10-03', 'Crème & Co', '-21,03']
['2026-10-04', 'Électricité Nord', '-28,04']
['2026-10-05', 'Boulangerie Rémi', '-35,05']
['2026-10-06', 'Pâtisserie Zoé', '-42,06']
['2026-10-07', 'Laiterie Hélène', '-49,07']
['2026-10-08', 'Épicerie Noël', '-56,08']
['2026-10-09', 'Farine Frères', '-63,09']
['2026-10-10', 'Sucre Doré', '-70,10']
['2026-10-11', 'Fourniture Gérard', '-77,11']
['2026-10-12', 'Loyer Été', '-84,12']
```
