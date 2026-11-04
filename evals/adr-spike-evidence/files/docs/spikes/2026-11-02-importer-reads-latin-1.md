---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 💡 Answered
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

Yes provided the importer opens the file as Latin-1: run 1 read all 12 of 12 transactions, each payee's name as the statement shows it.

## Surprises

None.

## Where it goes

- Spec: Nothing.
- ADR: reading the bank's file as Latin-1 is a choice, for an ADR.

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
