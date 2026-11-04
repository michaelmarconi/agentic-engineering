---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 💡 Answered
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

No. Run 1 stopped on the first payee with an accent, `Café Lune`: the file is not UTF-8, so the importer reads none of the 12 transactions.

## Surprises

None.

## Where it goes

- Spec: the statement import spec states that the bank's file is not UTF-8, so the importer can't read it as it comes.
- ADR: how to read the file's character encoding is a choice, for an ADR.

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

### Run 1

2026-11-04 15:12 UTC, Linux 6.18.44-fc-v233, your machine, code `3f18cef3cf35`, exit code 1

```
Traceback (most recent call last):
  File "/tmp/tmpe_3ygep_/data/spikes/e973e5422628-2026-11-02-importer-reads-bank-file/check_statement.py", line 6, in <module>
    rows = read_statement("samples/statement.csv")
  File "/tmp/tmpe_3ygep_/data/spikes/e973e5422628-2026-11-02-importer-reads-bank-file/src/importer.py", line 9, in read_statement
    return [row for row in csv.reader(f, delimiter=";")][1:]
                           ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "<frozen codecs>", line 325, in decode
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 32: invalid continuation byte
```
