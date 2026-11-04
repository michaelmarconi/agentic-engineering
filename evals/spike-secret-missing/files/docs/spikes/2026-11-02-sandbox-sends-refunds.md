---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 🟢 Ready to run
---

# Can the bank's test system send a refund?

## Question

Can the bank's test system send a refund through its refunds address?

## What would answer it

Each of 3 refund requests of 1.00 gets status 201 and a refund number in the reply.

## Experiment

Sends a refund request of 1.00 to the test system and prints the reply. It is sent over the network, so it runs three times.

- Runs: 3
- Stop early if: the reply's status is 404, which shows the test system has no refunds address.
- Starts from commit: None.
- Inputs: None.
- Secrets: `BANK_API_KEY`
- Command: `python3 check_refund.py`

## Answer

## Surprises

## Where it goes

## Open questions

- None.

## Code

```python
# file: check_refund.py
import json
import os
import urllib.request

key = os.environ["BANK_API_KEY"]
request = urllib.request.Request(
    "https://sandbox.bank.example/v1/refunds",
    data=json.dumps({"amount": 100}).encode(),
    headers={"Authorization": "Bearer " + key},
)
with urllib.request.urlopen(request) as response:
    print(response.status, response.read().decode())
```

## Runs
