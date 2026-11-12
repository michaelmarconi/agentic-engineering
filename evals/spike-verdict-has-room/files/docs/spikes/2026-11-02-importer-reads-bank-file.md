---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spike
status: 🟢 Ready to run
---

# The importer reads the bank's statement file as the bank sends it

## Hypothesis

The importer, as it stands, reads the bank's monthly statement file without anyone converting it first. The statement import spec waits on this, in its open questions: it cannot say whether the accounts clerk uploads the file as it arrives, or must first open it and save it again in another form, until we know.

## Finding

## Next steps

## How we'll know

The importer reads all 12 transactions in the sample statement without an error, and prints each payee's name as the statement shows it, accents and all. Reading fewer than 12 transactions, stopping with an error, or printing any payee's name with a letter changed or missing refutes the hypothesis. Nothing else counts: how fast it reads the file, and how the rows look on screen, do not matter here.

## Out of scope

- One month's statement stands for every statement the bank sends. The bank has sent its statements in the same layout for as long as the accounts clerk remembers, but it could change the layout without telling us.
- Only reading the file is tested. Adding the transactions to the ledger, checking amounts and spotting a statement uploaded twice are left to the spec's other requirements.
- The file is read on one computer. A computer set up for another language could read the same file differently, and that is not tested.
- Statements from other banks are not tested, since the spec covers only this bank.
- Very large statements are not tested. The biggest statement the clerk has had held about 400 transactions, and the importer reads the whole file at once, so size is unlikely to matter, but a far larger file might.

## How the test works

1. Take a real statement from last month, as the bank emailed it, and remove the account number, changing nothing else in the file: no letters, no line endings and no layout.
2. Read it using the importer's own code as it stands today, without changing a line, so the result says what the clerk would see if they uploaded it now.
3. Print how many transactions it read, then each transaction in turn, with its date, payee and amount.
4. Compare the count with the 12 transactions on the paper copy of the statement, and each payee's name with the paper copy, letter by letter.

This tests the hypothesis because it gives the importer exactly what the bank sends and nothing else, and checks the two things the clerk would notice: missing transactions and wrongly spelled payees. Several payees on this statement have accented letters, such as the café the office buys lunch from, so a file the importer cannot read properly would show up in their names.

Reading a file gives the same result every time, so one run is enough. A second run would read the same bytes with the same code and could not show anything new.

## Risks and safeguards

- The sample is a real statement, so it holds real payees and amounts. Its account number was removed before it was added to the repository, and nothing else in it identifies the company's account.
- The experiment only reads the file, on this machine. It writes nothing, sends nothing anywhere and does not touch the ledger, so it cannot change any real record.
- The printed transactions appear in the run's output, which is kept in this record. They hold nothing that is not already in the sample file.

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
