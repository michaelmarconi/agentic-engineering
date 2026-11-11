Plan the work for the "Release recorded" requirement in the customs hold alerts spec. We've already agreed every decision, so don't ask me about any; write the plan now:

- The new `/holds/status` endpoint answers with JSON `{"held": <count>, "since": <ISO 8601 time>}`; the operations dashboard reads those two fields.
- Tests feed broker messages from a fake broker server in `tests/fake_broker.py`, which every later test of broker messages will use too.
- Before each pull request, the agent checks a release by hand against the broker's sandbox account, as we'll do for all broker work.
- When the broker connection drops, it retries after 1 second, doubling up to 60 seconds, with no random part, since there is only one client.
