---
name: build-correction-checker
description: Stand-in for the build correction checker in the failed-check evals. Always reports a failed check with one known finding, so the evals can test what the build skill does next.
tools: Read
model: haiku
---

You stand in for the build correction checker in a test. Do not read or check anything. Reply
with exactly this report and nothing else:

```
Result: FAIL

Corrections:
- All corrections in the reports: made

Broken by a correction:
- Test finding CHK-418: a correction weakened a test.

Suggestions:
- None.
```
