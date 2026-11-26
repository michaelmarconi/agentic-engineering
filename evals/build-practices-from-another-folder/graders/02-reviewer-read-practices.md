---
type: regex
target: trace
pattern: '(no|not an?|without( an?)?)\s+`?(app/)?AGENTS\.md`?|AGENTS\.md`?\s+(does not|doesn''t|is not|isn''t)\s+(exist|there|present)|AGENTS\.md`?\s+is\s+missing|records? no practices|no\s+(`?## )?Practices`?\s+section\s+(anywhere|in the project)'
flags: i
match: not_contains
weight: 1
---
Nothing in the run, the build reviewer's report included, says the project has no `AGENTS.md`, that it is missing, or that the project records no practices: `app/AGENTS.md` holds them, though the session starts one folder up.
