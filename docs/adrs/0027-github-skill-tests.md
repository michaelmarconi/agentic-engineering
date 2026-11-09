---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
date: 2026-11-09
---

# Test skills that use GitHub against a fake `gh` command

## Question

How do the plugin's automated tests check a skill that reads and writes a GitHub pull request,
without a real pull request on GitHub?

## Decision

Chosen: a fake `gh` command, a small working stand-in that answers from a sample pull request
kept with the test. The test's checks look at what Claude achieved, not the route it took.

## Background

The plugin's skills are tested by cases that Claude Code's own test runner runs and scores, as
[ADR 0006](0006-skill-test-layout.md) decides. The markup skill reads review comments, replies to
them and resolves them on GitHub, as [ADR 0025](0025-document-markup-place.md) decides. The test
runner keeps each case away from the network, so a case cannot reach GitHub.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| A fake `gh` that answers and keeps state | Chosen | Tests what Claude achieved, whatever route it took |
| A mock `gh` that expects a fixed list of calls | Rejected | Fails whenever Claude finds another valid route |
| A real test repository on GitHub | Rejected | The test runner blocks the network, and runs would share state |
| The test runner's built-in fakes of tool services | Rejected | They cover only services a plugin provides itself, and GitHub's are not the plugin's |

## Consequences

- Good: the cases run offline, quickly and cheaply, at about six cents a run when tried.
- Good: any later skill that uses GitHub can copy the fake into its own cases.
- Bad: the fake answers only the calls it was written for, so a new call needs adding to it.
- Bad: every test run must be started so that a case's own `bin` folder comes before the real `gh`.

## Out of scope

- Committing inside a test, which the test runner does not allow.
- A skill's commit step is tested by its own script's unit tests instead.
- How closely the fake matches GitHub; a trial of the installed plugin against real GitHub covers that.

## How we'll check

Applies to: the test cases of any skill that reads or writes GitHub.

1. Test: a case passes only when Claude replies, resolves and refrains from merging as asked.
2. Inspection: the plugin's documented test command puts a case's `bin` folder first.
3. Test: the fake's own unit tests check each call it answers.

## Open questions

- None.

## Technical detail

**The fake.** A Python script named `gh`, in each case's `files/bin/`, answers the calls the skill
needs: `auth status`, `pr view`, and `api` for review comments, replies, reviews, merges and the
`graphql` queries that list and resolve review threads. Anything else exits with an error that
names the call. The test runner copies a case's `files/` into the folder Claude works in, so
`bin/gh` sits there. The fake seeds its state from the case's `.fakegh/state.json` into
`/tmp/fakegh/`, because a test may write to `/tmp` but not to its own folder. Merges are recorded,
never done.

**The command path.** A case file may set only variables named `EVAL_*`, and the working folder's
settings file is ignored, so neither can put the fake first. The documented test command in
`AGENTS.md` therefore starts `PATH="bin:$PATH" claude plugin eval …` for every skill. Cases
without a `bin/` folder are unaffected.

**Scoring.** Graders search the run's trace, which records every command and its output, with
`target: trace`, and read the files Claude edited.

**Evidence.** On 9 November 2026 a throwaway case gave Claude, with no skill loaded, a document
and a fake holding two review comments: a wording change and a question. Claude found and used
the fake unprompted. All five checks passed: the wording was applied, both comments got replies,
the first thread was resolved, and nothing was merged.
