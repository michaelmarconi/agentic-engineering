# `/build`

`/build` is the skill for building one plan. It is one step of [the lifecycle](../lifecycle.md); read
that page first for the documents, skills and agents it mentions.

## What `/build` does

`/build` takes one plan that you have signed off, or that you choose to build before sign-off,
and writes the code and tests it describes on a
branch of its own, has the result reviewed, and hands the branch back to you.

```mermaid
flowchart TD
    Check[Checks before starting] -->|a check fails| Stop[Stop and say why]
    Check -->|not signed off| Ask[Ask: build anyway?]
    Ask -->|stop| Stop
    Ask -->|build anyway| Build
    Check --> Build[Build on its own branch, tests first]
    Build --> Review[Three reviews]
    Review -->|all passed| Built[Mark the plan Built]
    Review --> Correct[Correct once, then check the corrections]
    Correct -->|passed| Built
    Correct -->|findings open| Walk[Go through them with you]
    Walk -->|you say Built| Built
    Walk -->|you stop| Hand
    Built --> Hand[Hand over the branch]
    Hand -.->|you| Verify[Verify, then merge]
```

## Your practices, and where `/build` stops

`/build` follows your project's practices: how to set up, build, test and run the product, how
branches and commits are named, and what must pass before work is merged. It reads them where
`/plan` does: the `## Practices` section of `AGENTS.md` and of `CLAUDE.md`, whichever have one, and
the files under `docs/practices/` they name, whether or not `CLAUDE.md` imports
`AGENTS.md`,[^memory] and its reviewer reads the same. The `/practices` skill, run whenever you want
to record or change a practice, asks you about them and records them under a `## Practices` heading
in `AGENTS.md`, with longer topics in `docs/practices/`, and makes sure `CLAUDE.md` imports
`AGENTS.md`. A choice between alternatives, such as which test framework to use, is an ADR
(architecture decision record) instead.

`/build` stops once it has handed the branch back. These steps stay with you, done the way your
practices say, because each needs a person:

- **Verifying:** starting the product and using it, the way a person would, to check it does
  what the specs say. A build may run on a machine that cannot run the product, so this is a
  separate step: run [`/verify`](verify.md) where the product can run.
- **Opening a pull request**, if you use them.
- **Merging** the branch into the main branch.

## Before it starts

Run `/agentic:build docs/plans/<plan>.md`, best as the first thing in a new session. Before it
changes anything, `/build` checks:

- **The session is clean enough.** A long planning conversation is a poor start for building:
  Anthropic's own advice is to start a fresh session to build from a written spec,[^fresh] so the
  build begins from the written definition of done rather than the talk that led to it. So when you
  ask for a build, whether you type the command or ask in your own words, a plugin hook measures how
  much conversation the session has gained since Claude's first reply. Under 20,000 tokens (roughly
  15,000 words) the build starts. Over it, `/build` asks you one question: build here anyway, or
  start clean. Starting clean gives you two steps, since the plugin has no reliable way to start a
  new session for you: run `/clear`, then send `/agentic:build docs/plans/<plan>.md`. In a Claude
  project, a new session is a new thread: open one and send that command as its first message. A
  thread that Claude opened for you can build straight away, as long as it hasn't done much else
  first ([ADR 0037](../adrs/0037-build-session-check.md)).
- **The plan exists and can be built.** A `Built ✅` plan is refused: a plan is built once. Every
  spec and ADR the plan names must exist, with a heading for each requirement it names, and none
  may be `Rejected ❌` or `Superseded ↪️`. These can't be overridden, since there would be nothing
  to build against.
- **The plan is signed off, or you choose to build anyway.** If the plan, or a spec or ADR it
  names, is `Draft 📝`, `/build` doesn't refuse. This is its last check, so a build you choose to
  go on with isn't then stopped by another. It lists what
  isn't signed off, including the plan's open questions, and asks "Build anyway, on the proposed
  answers?". Building before sign-off is your call: pick "Build anyway" and it builds each open
  question's proposed answer, or "Stop and settle them first" and it changes nothing. It never
  builds an unsigned plan without your answer, so an unattended run stops. The build's first
  commit says what wasn't signed off and how each open question was answered, so the record is in
  git, and the plan keeps its status.
- **Your practices, if any.** `/build` looks for the `## Practices` heading, and reads any file
  it names to read before a task like this. None is required:
  where a practice it needs is not recorded, such as how to run the tests, it works it out from
  your repository and carries on, and its report says what it assumed and suggests `/practices`
  to record it.
- **It is on a branch of its own, with nothing left uncommitted.** `/build` never builds on your
  repository's default branch. If you are on it, it makes a branch named as your practices say,
  or else after the plan. If you are already on another branch, it builds there, since some
  places that run Claude Code, such as its cloud sessions, choose the branch name for you. If anything is uncommitted, it stops, so your
  own work never gets mixed into the build. It ignores the stand-ins for `/dev/null` that Claude
  Code's sandbox puts in place of files it protects, such as `.bashrc`, on Linux. While it runs, a plugin hook refuses any commit or
  push to the default branch.
- **It has a remote.** The repository needs a remote named `origin` whose default branch git
  knows, which `git clone` sets up. `/security-review` compares the branch with that default
  branch, and the hand-over pushes to it. If it is missing, `/build` stops and names the command
  to run, such as `git remote set-head origin -a`; it never runs that itself, since it would
  change your repository.
- **The reviews can run.** Claude must be allowed to start `/code-review` and `/security-review`,
  which a setting can turn off. If either is not, `/build` stops and says which, so every build
  gets all three reviews.

Finally, it runs your tests once. Any test that already fails is noted for the report, and
`/build` does not try to fix it.

## Building

`/build` works through the requirements the plan names. For each one, it first writes tests from
the spec's examples, then writes the code that makes them pass. Before writing any of the code, it
runs a small script on the new tests, which accepts them only if each new or changed test file
fails and nothing else is uncommitted. Tests that already pass can't show the new code works, and
code written before its tests shows up as uncommitted work or as tests that already pass. If the
code was already committed, such as by an earlier build that stopped, `/build` keeps the tests and
reports the refusal, and the review names that requirement so you can decide whether to accept it
([ADR 0039](../adrs/0039-tests-fail-without-code.md)). It then runs
your whole test suite and your linters, as your practices say, before moving on, so it notices at
once if the new code breaks something already built. It follows every `Accepted 👍` ADR the plan
names, and any other whose How we'll check section says it applies to the code being changed. It
commits as it goes, so the branch always holds the work so far.

Two rules hold throughout:

- **A test is never weakened to make the code pass.** `/build` changes a test only to make it
  check its example more closely, or to correct an expected value that plainly contradicts the
  spec, such as a typo, which its report then points out.
- **Two attempts, then stop.** If a requirement's tests still fail after two attempts, `/build`
  stops and hands over with the failure written down, rather than keep retrying an approach that fails.
  Anthropic gives the same advice: after two failed corrections, start again rather than try a
  third.[^twice]

A long build can run for hundreds of thousands of tokens, and what Claude read at the start carries
less weight the further back it sits in the conversation. So each time the tests script checks a
requirement's new tests, before any of its code is written, it prints your `## Practices` sections
and the build's own rules again, and only those: not the rest of `AGENTS.md`, nor the topic files
under `docs/practices/`. That costs about 1,500 tokens each time. It keeps the rules in view, but can't guarantee they are followed, so
a rule that must hold, such as tests first, also has a script that checks it.

If a build stops halfway, for whatever reason, start a new session on the same branch and run
`/build` with the same plan again. It reads what the branch already holds, compares it with the
plan and carries on.

### Decisions

A plan cannot foresee everything, so `/build` meets choices as it goes. It may make a choice itself
only if the choice would not need an ADR or a change to a spec. That means it raises any choice
that would:

- be a lasting choice between real alternatives, such as a library, a data format, or the shape
  of an interface: that is what an ADR is for, and only you accept ADRs;
- change what a user sees in a way the spec does not settle;
- be hard to undo later, such as a database schema, a public interface, or data already stored;
- stretch or contradict a spec, an ADR, or your practices.

To raise one, `/build` stops and hands over with the question written down. It never guesses. A
guess can carry a long build down the wrong path before anyone looks.[^assumption]

Every other choice, such as names, how the code is split up, which helper to use, the wording of
an error message or an exit code, `/build` makes itself and carries on, and the report lists
each one with its reason, so you can see what was decided for you.

`/build` leans towards correcting rather than asking. Anything plainly wrong, such as a crash
when no file name is given or an error reported in the wrong place, it corrects whether or not a
spec mentions it, with a test where it can, and lists each correction in its report so you can
add it to the spec. Stopping a build to ask about something obvious costs more than a small
overstep. It raises the case with you only when what should happen instead is a real product
choice that a reasonable person could want made differently.

## Review

When the code is written, three reviews check it side by side, each run by an agent that has not
seen the conversation:

- **Code:** Claude Code's own `/code-review`,[^codereview] looking for bugs. `/build` always runs
  it at `medium` effort, and always compares the whole branch with the main branch, so a rerun
  reviews the whole build, not just its latest commits.[^localreview] `/build` starts it inside an
  agent, as it does the security review, because some Claude Code versions run the skill inside
  the session rather than in a fresh agent of its own, and only an agent's report reliably reaches
  the plugin's hook that hands the reports to the correction check.
- **Security:** Claude Code's own `/security-review`, looking for security holes.
- **Plan:** the plugin's build reviewer, `agents/build-reviewer.md`. It checks that each requirement the plan names is built,
  with a test that checks each of its examples as the spec words it; that nothing unrequested was
  added; that the code follows the ADRs it must; and that no choice that should have been raised
  was made quietly. This is the review Anthropic suggests writing yourself: against your spec,
  reporting gaps that affect correctness and skipping style.[^specreview]

A reviewer asked to find problems will always find something, so the reviews pass once every bug
or security hole they report has been corrected. Findings about tidiness or style are listed in the
report but do not stop the plan being marked `Built ✅`.[^specreview]

`/build` corrects what the reviews find, once, and has the corrections checked, the same way
documents are reviewed (see [Review process](../lifecycle.md#review-process)), but with its own
correction checker, `agents/build-correction-checker.md`, and no language checker, since it writes
code. It then runs your tests and linters again.

## Handing over

However the build ends, a small script commits the branch and pushes it to `origin`. It does
this, not Claude, and reports exactly what happened, including the branch name and any failure
to push. `/build` never opens a pull request and never merges.

Every hand-over also leaves a draft release note for the people who use the product: a line
starting `Release-note:` at the end of the last commit's message, one per thing they would
notice, such as `Release-note: You can now export your mail as CSV.` Claude drafts each from the
plan's requirements as the specs state them, while they are in hand. [`/release`](release.md)
gathers these lines from every commit since the last release, so its notes don't depend on the
plan still existing or on its status, and your repository needs no extra file
([ADR 0043](../adrs/0043-build-commit-carries-release-note.md)). If there is nothing left to
commit, the script makes a commit that holds only the notes.

The plan is set to `Built ✅` only when it was `Ready to build 🟢` and either every review passed
or you settled what they left open, as below. A plan built before sign-off keeps its status:
settle it and sign it off, then rerun `/build` on the branch to mark it `Built ✅`. If the build
stopped before its reviews, because a requirement's tests still failed after two attempts or a
choice needed raising, the plan keeps its status: sort out what is open, then rerun `/build` on
the branch, which resumes and reviews afresh.

### When the reviews leave findings open

The reviews read whole files, so they can also report problems in older code that this build did
not change, such as an untouched part of a file it added one line to. The correction checker sorts
what is open into two groups: the build's own findings, and findings **outside this build**. To
tell them apart, a plugin hook gives it the lines the build changed, file by file, such as
`src/parser.ts: 40-52, 88`, and it grades each outside finding high, medium or low. Outside
findings never fail the check on their own.

```mermaid
flowchart TD
    Check[Correction check] --> Ask[One question per finding]
    Ask --> Fix[Fixes made on the branch]
    Fix --> Recheck[Check only what changed]
    Recheck -->|raises more| Ask
    Recheck -->|the build's own are done| Summary[Outside this build: how many, how severe]
    Summary -->|go through them| Ask
    Summary -->|carry on| Last[Last question]
    Last -->|Built| Built[Plan marked Built]
    Last -->|one more review| Reviews[Three reviews afresh]
    Last -->|stop| Ready[Plan stays Ready to build]
```

1. **The build's own findings, one at a time.** Each comes with a proposal, such as fixing it on
   the branch or dropping a test the code cannot meet, and the same four choices the document
   skills offer: **Accept** the proposal, give **your own answer**, **Ignore** it, accepting it as
   it is, or **Defer** it to a later plan. Fixes are made and committed on the branch as you go,
   with no review between answers.
2. **A check of only what changed.** When a round of answers changed the branch, the correction
   checker runs again on just those commits, with your answers, never a full review. Anything it
   raises is put to you the same way.
3. **Findings outside this build, in one question.** Rather than a question for each, `/build`
   says how many there are and how severe, such as "4 problems in older code outside this build:
   1 high, 2 medium, 1 low", and asks whether to go through them or carry on. Going through them
   works as in step 1; carrying on leaves them all open.
4. **The last question.** Mark the plan `Built ✅`, run one more full review of the whole branch,
   or stop with the plan still `Ready to build 🟢`. A full review runs only when you ask for one.
   `Built ✅` is offered however many commits your answers added: the hand-over script marks the
   plan at the commit last checked, and its commit message lists every finding you ignored,
   deferred or carried on past, so the pull request shows what you agreed to.

All of this happens in the same conversation as the build. Once the conversation is over, running
`/build` again on the branch reviews afresh.

It ends with a short reply, under 175 words: the outcome, the branch and whether the plan was
marked `Built ✅`, then at most five bullets of at most 15 words each, with the main findings and
any question or action for you, then the full path of the build's report file. Where the app
you run Claude Code in can show you a file, the report opens there. The file is Markdown, kept outside your repository
in the session's scratchpad, a temporary folder Claude Code gives each session, under
`agentic/reports/<repository>/`, named by date and plan, until Claude Code clears it; where the
session has no scratchpad, it goes in a private folder in your system's temporary folder instead. It holds:

- what was built, or why it stopped and what is open;
- for a build before sign-off, what was not signed off and the answers it built on;
- the test and lint commands it ran, with their output, and any tests that were failing before it
  started;
- the decisions it made for you, each with its reason, and any defects it corrected that no spec
  mentions;
- what it corrected for each review;
- each review's report and the correction check's report, and the hand-over script's own report,
  copied in by the script word for word, so you read them exactly as they were given;
- what is left for you to check, and [`/verify`](verify.md) on the plan: as a step before merging
  if your practices say it must pass first, otherwise as an option.

A build that refuses to start, such as on a plan that is already built, writes no file: its reply
says why.

## After a build

A `Built ✅` plan is frozen: it is never edited again, and you may delete it whenever nobody needs
it, since nothing refers to a plan. [`/audit`](audit.md) lists built plans you might delete. For
more work on the same requirements, write a new plan, or make small corrections by working with
Claude directly, which is the usual way to tidy up after a large build.

A spec's status does not change when it is built. It describes the document, not the software,
because a status about the software would stop being true, without anyone noticing, as the code
changes. To find out whether the software meets a spec, check the software against it with
[`/verify`](verify.md).

[^fresh]: Claude Code documentation, [Best practices: brainstorm with Claude first](https://code.claude.com/docs/en/best-practices#brainstorm-with-claude-first):
    "Once `SPEC.md` exists, start a fresh session to build from it, so the build begins with a
    clean context and a written definition of done."
[^codereview]: Claude Code documentation, [Best practices: give Claude a check to run](https://code.claude.com/docs/en/best-practices#give-claude-a-check-to-run):
    `/code-review` "reviews the diff in a fresh subagent that never saw your conversation".
[^specreview]: Claude Code documentation, [Best practices: review against your spec](https://code.claude.com/docs/en/best-practices#review-against-your-spec).
[^twice]: Claude Code documentation, [Best practices: steer the session](https://code.claude.com/docs/en/best-practices#steer-the-session):
    "after two failed corrections run `/clear` and write a better prompt instead of a third."
[^assumption]: Claude Code documentation, [Best practices: let Claude run without you](https://code.claude.com/docs/en/best-practices#let-claude-run-without-you):
    "you find out the next morning that it spent the whole night building on the wrong assumption."
[^localreview]: Claude Code documentation, [Review locally with /code-review](https://code.claude.com/docs/en/code-review-local).
[^memory]: Claude Code documentation, [How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md).
