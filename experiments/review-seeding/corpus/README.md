# Review-seeding corpus

This corpus was written for an experiment that measures how many planted defects a spec
reviewer catches. It describes Rallybook, an invented court-booking app for small UK tennis
clubs: `product/docs/brief.md` is its product brief and `product/docs/specs/` holds three
clean background specs (member invitations, court booking, booking cancellation), each
written to pass every check in the `/spec` rubric. Each case under `cases/` adds one more spec
(`spec.md`, status Draft, for a capability none of the background specs covers) that is placed
at the `spec_path` given in its `case.json`, next to the background specs and the brief, which
is everything the reviewer reads. `clean-01` and `clean-02` are meant to pass every rubric
check and carry no defects; `seeded-01` to `seeded-08` each carry 2 or 3 planted defects and
are otherwise written to pass the rubric. Every defect is detectable from the spec, the
rubric, the brief and the background specs alone, is written to read naturally with no marker
in the text, and is recorded in `case.json` with its type, its subtlety (obvious, or subtle:
plausibly missed on a first careful read), the exact text where it sits and what a reviewer
must point out to count as having caught it. The corpus was written without reading the
reviewer's prompts.

| Case | Defect | Type | Subtlety |
|---|---|---|---|
| seeded-01 | seeded-01-a | ambiguous-rule | subtle |
| seeded-01 | seeded-01-b | conflicts-with-other-spec | subtle |
| seeded-01 | seeded-01-c | how-not-what | obvious |
| seeded-02 | seeded-02-a | conflicts-with-brief | obvious |
| seeded-02 | seeded-02-b | one-sided-limit | subtle |
| seeded-03 | seeded-03-a | solution-in-problem | obvious |
| seeded-03 | seeded-03-b | scenario-contradicts-rule | subtle |
| seeded-03 | seeded-03-c | internal-contradiction | subtle |
| seeded-04 | seeded-04-a | conflicts-with-brief | obvious |
| seeded-04 | seeded-04-b | unverifiable | obvious |
| seeded-05 | seeded-05-a | unstated-outcome | subtle |
| seeded-05 | seeded-05-b | conflicts-with-other-spec | subtle |
| seeded-05 | seeded-05-c | how-not-what | obvious |
| seeded-06 | seeded-06-a | conflicts-with-brief | subtle |
| seeded-06 | seeded-06-b | scenario-contradicts-rule | obvious |
| seeded-06 | seeded-06-c | ambiguous-rule | subtle |
| seeded-07 | seeded-07-a | internal-contradiction | obvious |
| seeded-07 | seeded-07-b | unstated-outcome | subtle |
| seeded-07 | seeded-07-c | solution-in-problem | subtle |
| seeded-08 | seeded-08-a | one-sided-limit | subtle |
| seeded-08 | seeded-08-b | unverifiable | obvious |
