---
type: llm
focus: { source: file, path: docs/plans/2026-10-20-customs-hold-release.md }
weight: 1
---
The plan's Open questions holds the fake broker, the /holds/status answer and the check by hand, each naming the ADR, spec change or practice to record, and Decisions no longer lists them. Each ends with a "Proposed:" that keeps the decision as it was (a fake broker server in tests/fake_broker.py, the {"held", "since"} answer, the check by hand against the sandbox account), not one that drops or replaces it; doubts about a decision may appear in the question's text. PASS if so, FAIL otherwise.
