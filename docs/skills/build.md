# `/build`

*Not built yet. This page describes the agreed design.*

`/build` is the skill for building one plan. It is one step of [the SDLC](../../README.md); read
that page first for the documents, skills and agents it mentions.

## What `/build` does

`/build` takes one plan that you have signed off, writes the code and tests it describes on a
branch of its own, has the result reviewed, and hands the branch back to you.

```mermaid
flowchart LR
    Check[Check before starting] --> Branch[Use or make a build branch]
    Branch --> Build[Build: tests first, commit as it goes]
    Build --> Review[Three reviews]
    Review --> Correct[Correct once, then check the corrections]
    Correct --> Hand[Mark the plan Built and hand over]
    Hand -.->|you| Verify[Verify, then merge]
    Verify ~~~ Pad["#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;#nbsp;"]
    style Pad fill:none,stroke:none
```

## Your practices, and where `/build` stops

`/build` follows your project's practices: how to set up, build, test and run the product, how
branches and commits are named, and what must pass before work is merged. It finds them where
Claude Code finds any project instructions: in `CLAUDE.md`, or in `AGENTS.md` when there is no
`CLAUDE.md` or when `CLAUDE.md` imports it.[^memory] Where the project says nothing, `/build` works
it out from the repository, as Claude does for any task, and says in its summary what it assumed.
A later skill, `/practices`, will ask you about your practices and write them down. A choice
between alternatives, such as which test framework to use, is an ADR (architecture decision
record) instead.

`/build` stops once it has handed the branch back. These steps stay with you, done the way your
practices say, because each needs a person:

- **Verifying:** starting the product and using it, the way a person would, to check it does
  what was asked. A build may run on a machine that cannot run the product, with nobody
  watching, so this is a separate step. Claude Code's own `/verify` does it.[^verify]
- **Opening a pull request**, if you use them.
- **Merging** the branch into the main branch.

## Before it starts

Run `/sdlc:build docs/plans/<plan>.md` as the first thing in a new session. Before it changes
anything, `/build` checks:

- **The session is fresh.** `/build` runs only in a session that started with `/build`. A long
  planning conversation is a poor start for building: Anthropic's own advice is to start a fresh
  session to build from a written spec,[^fresh] so the build begins with a clean context and a
  written definition of done. A plugin hook enforces this by checking how much the conversation
  has grown, and if it refuses, it says why and asks you to start a new session. In a Claude
  project, a new session is a new thread.
- **The plan is ready.** It is `🟢 Ready to build`. A `✅ Built` plan is refused: a plan is built
  once.
- **Nothing it relies on has changed.** Every spec the plan names is still `👍 Accepted`, and every
  ADR is still `👍 Accepted`. If one has changed since you signed the plan off, `/build` stops and
  says which.
- **It is not on the main branch.** `/build` never builds on your repository's default branch. If
  you are on it, it makes a branch named after the plan. If you are already on another branch, it
  builds there, since some places that run Claude Code, such as its cloud sessions, choose the
  branch name for you.

## Building

`/build` works through the plan's steps. For each requirement the plan names, it first writes
tests from the spec's scenarios and sees them fail, then writes the code that makes them pass. It
follows every `👍 Accepted` ADR the plan names, and any other whose Confirmation section says it
applies to the code being changed. It commits as it goes, so the
branch always holds the work so far.

If a build stops halfway, for whatever reason, start a new session on the same branch and run
`/build` with the same plan again. It reads what the branch already holds, compares it with the
plan and carries on.

## Review

When the code is written, three reviews check it side by side, each run by an agent that has not
seen the conversation:

- **Code:** Claude Code's own `/code-review`,[^codereview] comparing the branch with the main branch,
  looking for bugs.
- **Security:** Claude Code's own `/security-review`, looking for security holes. It needs the
  repository to have a remote; without one, `/build` skips it and says so.
- **Plan:** the plugin's build reviewer. It checks that each requirement the plan names is built,
  with a test for each of its scenarios; that nothing unrequested was added; and that the code
  follows the ADRs it must. This is the review Anthropic suggests writing yourself: against your
  spec, reporting gaps that affect correctness and skipping style.[^specreview]

`/build` corrects what the reviews find, once, and has the corrections checked, the same way
documents are reviewed (see [Review process](../lifecycle.md#review-process)). If the check fails,
`/build` stops and shows you the reports.

## Handing over

When the reviews pass, `/build` sets the plan to `✅ Built`, commits, and pushes the branch if the
repository has a remote. A small script does this, not Claude, and reports exactly what happened,
including the branch name and any failure to push. `/build` never opens a pull request and never
merges.

It ends with a short summary: what was built, what the reviews found and what was corrected, and
a reminder to verify the work before merging.

## After a build

A `✅ Built` plan is kept as a record of what was built and how, like a superseded ADR. It is never
edited again, and nothing deletes it. For more work on the same requirements, write a new plan,
or make small corrections by working with Claude directly, which is the usual way to tidy up after
a large build.

A spec's status does not change when it is built. It describes the document, not the software,
because a status about the software would stop being true, without anyone noticing, as the code
changes. To find out whether the software meets a spec, check the software against it.

[^verify]: Claude Code documentation, [Run and verify your app](https://code.claude.com/docs/en/skills#run-and-verify-your-app).
[^fresh]: Claude Code documentation, [Best practices: brainstorm with Claude first](https://code.claude.com/docs/en/best-practices#brainstorm-with-claude-first):
    "Once `SPEC.md` exists, start a fresh session to build from it, so the build begins with a
    clean context and a written definition of done."
[^codereview]: Claude Code documentation, [Best practices: give Claude a check to run](https://code.claude.com/docs/en/best-practices#give-claude-a-check-to-run):
    `/code-review` "reviews the diff in a fresh subagent that never saw your conversation".
[^specreview]: Claude Code documentation, [Best practices: review against your spec](https://code.claude.com/docs/en/best-practices#review-against-your-spec).
[^memory]: Claude Code documentation, [How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md).
