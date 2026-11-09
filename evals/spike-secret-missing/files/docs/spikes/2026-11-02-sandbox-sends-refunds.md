---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: Spike
status: 🟢 Ready to run
---

# The bank's test system sends a refund

## Hypothesis

The bank's test system sends a refund when asked through its refunds address.

## Finding

## Next steps

## How we'll know

Each of 3 refund requests of 1.00 gets status 201 and a refund number in the reply.

## Out of scope

- The test system stands for the live one; the live system may behave differently.

## How the test works

1. Send a refund request of 1.00 to the bank's test system.
2. Print the reply's status and body.

The request goes over the network, where a reply can vary, so it runs three times.

## Risks and safeguards

- It could move real money: it sends requests only to the bank's test system, which moves none.
- It could reveal the bank's key: the key is read from the environment and never printed or saved.

## Results

## Surprises

## Open questions

- None.

## Experiment

`check_refund.py` posts `{"amount": 100}`, 1.00 in cents, to `https://sandbox.bank.example/v1/refunds`, the test system's address, with the key from `BANK_API_KEY` in the `Authorization` header, and prints the status and body. It holds when all three runs print `201` and a refund number; a `404` shows there is no refunds address.

- Runs: 3
- Stop early if: the reply's status is 404, which shows the test system has no refunds address.
- Starts from commit: None.
- Inputs: None.
- Secrets: `BANK_API_KEY`
- Command: `python3 check_refund.py`

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
