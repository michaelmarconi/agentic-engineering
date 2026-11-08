---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to run
---

# The importer reads the bank's statement file as the bank sends it

## Hypothesis

The importer, as it stands, reads the bank's monthly statement file without anyone converting it first. The statement import spec waits on this, in its open questions.

## Finding

## Next steps

## How we'll know

The importer reads all 12 transactions in the sample statement without an error, and prints each payee's name as the statement shows it.

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

Imports `read_statement` from `src/importer.py` at the commit below and reads `samples/statement.csv`, a real statement with the account number removed. It holds when the script prints `12 transactions read` and every payee's name as written, such as `Café Lune`; an error, or fewer rows, refutes it.

- Runs: 1
- Stop early if: None.
- Starts from commit: `@COMMIT@`
- Inputs: `samples/statement.csv`
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

### Run 1

2026-11-04 15:12 UTC, Linux 6.18.44-fc-v233, your machine, code `3f18cef3cf35`, exit code 1

```
Traceback (most recent call last):
  File "/tmp/tmpvm7hiz55/data/spikes/9d3a16cbe7f9-2026-11-02-importer-reads-bank-file/check_statement.py", line 6, in <module>
    rows = read_statement("samples/statement.csv")
  File "/tmp/tmpvm7hiz55/data/spikes/9d3a16cbe7f9-2026-11-02-importer-reads-bank-file/src/importer.py", line 9, in read_statement
    return [row for row in csv.reader(f, delimiter=";")][1:]
                           ~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "<frozen codecs>", line 325, in decode
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 32: invalid continuation byte
```
