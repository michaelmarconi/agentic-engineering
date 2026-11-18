---
name: practices
description: Record how a project does things, for coding agents to follow, one topic at a time, in a short Practices section of AGENTS.md and topic files under docs/practices/, such as the commands that set it up, run it and test it, branch and commit rules, what must pass before merging, and files never to edit; give an overview of what is recorded and what is missing; improve recorded practices. Use whenever someone wants agents to know how to build, test, lint or release the project, wants to write down or change project conventions, standards or rules for agents, asks what practices are recorded, or wants a topic of their own recorded, even if they don't say "practices". Not for documents written for people, such as the README or a contributing guide, nor for a choice between technologies, which is an ADR.
---

# Practices

Practices are the facts and habits a coding agent needs to work on the project without asking:
how to set it up, run it and check its work, the rules it follows, and where to read more. They
are written for agents, not people, and have no status: they are corrected in place whenever the
way the project works changes.

They live in two layers, so an agent always has the essentials and reads detail only when its
task needs it:

- **The core**: the `## Practices` section of `AGENTS.md`, which Claude reads on every task. A
  new core starts from [assets/core.md](assets/core.md): three parts, Check your work, Rules, and
  Files to read before a task, each holding "None yet." until something is recorded there.
- **Topic files**: `docs/practices/<topic>.md`, one per topic with more to say than a line or two
  in the core, such as `testing.md`. The core names each one on its own line under Files to read
  before a task, saying which task calls for it: "before writing or changing tests:
  `docs/practices/testing.md`". A topic file names no further file the agent must read.

A plugin hook refuses an edit that takes the core past 50 lines or a topic file past 200, or that
adds an `@` import. If it refuses yours, move the detail into a topic file and leave one line in
the core.

Claude Code reads `AGENTS.md` reliably only when `CLAUDE.md` imports it with a line that is
exactly `@AGENTS.md`. If there is no `CLAUDE.md`, create one holding that line. If there is one
without the line, ask the person before adding it, since the file is theirs, and change nothing
else in it. That question waits for the hand-over: write the practices first.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it leaves less to correct. Write in plain words, as the Plain
words section of [the lifecycle page](../../docs/lifecycle.md#plain-words) says. Read these with
the Read tool, not the shell, so the person is not asked to approve a command.

## Read the repository first

Much of what the practices hold is already in the repository: build and dependency files, test
settings, continuous integration settings, the README, a contributing guide, the existing core and
topic files, and the ADRs in `docs/adrs/`. Read what bears on the topic before asking anything, so
you propose what you find and the person confirms rather than dictates. You may read the README
and other documents for people, but never change them unless the person explicitly asks.

## A bare run: the overview

When the person names no topic, give an overview and write nothing. Read
[references/topics.md](references/topics.md), and read the practices and the repository afresh
every time, even later in a conversation that has already read them, since either may have
changed outside it. Then list each topic by name as
recorded, not recorded yet, or out of step with the repository or with the one-command rule below, with a few words on why, such as
"tests exist, but no test command is recorded". When a recorded practice and the repository
disagree, such as a test command that differs from the one the CI file runs, say what each says
and ask which is right. Then suggest the one topic that matters most now, judged from the
repository and any plans in `docs/plans/` waiting to be built, and offer to start on it. Never
suggest a topic nothing needs yet, such as deployment when nothing is deployed. End by inviting
a topic of the person's own.

## One topic

With a topic, cover that topic alone and stop. The topics file says what each suggested topic
asks and where its answers usually go. A topic of the person's own, such as how decisions are
approved, works the same way: decide what to ask from what they want recorded, and give it a topic
file and a line in the core. When the topic is already recorded, start from what is there and
propose changes rather than starting again.

Use every answer the person has already given, and ask only what remains. When you have questions,
say how many, then ask only the first. Its context is a short summary of what it is about and what
the repository shows, so someone who does not know the repository can answer, and its proposal is
one they can accept, change or reject; give any examples as possible answers, not further questions.
When you ask the person to settle a question in the conversation, lay it out in four parts, so they
can find your proposal at a glance: a bold line naming it and its place in the count, such as
"**Question 2 of 7: how often a failed pull is retried**", where the first number counts the
questions asked or settled in this conversation, this one included, and the total adds those
still open, so the first number only goes up, and you say in one line when an answer opens new
questions; the context it needs; a block quote
holding a "**Proposed:**" line with your answer, a line holding only `>`, and a "**Why:**" line with
the reason; and the
question itself, last, in one line. Ask the next once the first is settled, saying the answer is
noted, not recorded: nothing is recorded until the files are written. If the person has said not to
ask, write what is settled and ask nothing. Otherwise, even when their answers covered everything,
finish the topic by asking whether there is anything else about it they want recorded, in the
hand-over if you have written the files: the topics file is only a starting point, and they know
what it misses. Being asked to ask only what you must does not waive this question; only being told
not to ask anything does.

- **No view.** When the person has no view on a question, ask whether to look up current advice
  on the web for their language and tools, rather than searching unasked. If they agree, name
  the sources you used. If they decline, or you cannot reach the web, say your proposal comes
  from Claude's own knowledge. Either way, a practice that is a default they accepted, rather than
  something they said or the repository shows, ends with "(default)".
- **Not answered.** A question the person declines to answer is left out entirely, never written
  as a guess, a hedge or a marker such as TODO, so the overview shows it as not recorded.
- **A choice between alternatives**, such as which language, framework, library or test framework
  to use, is not a practice. Say so, write nothing that makes the choice, and suggest recording
  it with `/adr`, where its reasons are kept and the person accepts it. A practice can still say
  how to use what an ADR chose, and a command for a tool the repository does not use yet ends with
  "(not set up yet)".
- **Secrets.** Never write a password, key or token, even when the person gives one and asks.
  Record where it lives instead, such as the environment variable and the store it comes from,
  and tell the person why.
- **Vague rules.** A rule must say what to do or not do, in a way an agent could follow or break.
  Turn a vague aim such as "write clean code" into such a rule with the person, or leave it out
  and tell them why. If they want it recorded exactly as they said it, write it so: the wording
  is theirs, and the review will raise it for them to decide.
- **Running the product.** Try it before writing it: once the person has said which services are
  safe to touch and which never are, start the product with the proposed commands, reach each
  interface it names, and stop it. When a step fails, show what it printed, correct the step with
  the person, and try again, until it runs and they agree. Record only what ran, and never touch a
  service they marked as never to be touched, even to try it. Agents that verify the product, and
  that never read its code, rely on this topic alone to start it.
- **Releasing and deploying.** `/agentic:release` and `/agentic:deploy` act on real systems from
  these topics alone and never ask, so write each in the exact headings the topics file gives and
  ask the required items first. A required item comes from the person or the repository, never a
  default you propose; an optional one may be a default. Draft each environment's check from
  Running the product when it is recorded, pointed at that environment's address. Try only what
  is safe: read the current version, run each check against the address the person gave for its
  environment, and run a publish or deploy command in its dry-run mode where it has one; never
  publish, deploy or roll back. When a try fails, show what it printed and settle the step with
  the person; if they said not to ask, record it as they gave it and name the failure in the
  hand-over. Before the review, run
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/practice_complete.py" <the topic file's path>`, the same
  test of complete those skills run, and name in the hand-over each item it lists as missing,
  since they refuse until it is there.
- **Pull request template.** Only in Reviews and merging, once the person says the project uses
  pull requests. The project is on GitHub when the `origin` remote in `.git/config` names
  `github.com` or a `.github/` folder exists; otherwise ask, or take it as not on GitHub if the
  person said not to ask. On GitHub, if a template already exists, named `pull_request_template.md`
  in any letter case, in `.github/`, the root or `docs/`, or in a `.github/PULL_REQUEST_TEMPLATE/`
  folder, leave it exactly as it is. Otherwise show
  [assets/pull_request_template.md](assets/pull_request_template.md) and, only on yes, write it to
  `.github/pull_request_template.md`. Then record the rule "Pull request descriptions follow
  `<the template's path>`." With no template, off GitHub or declined, the rule lists the default's
  sections instead, in one or two lines, saying that Built from names the plan, specs and ADRs.
  The rule goes in the core's Rules, since a topic file names no further file.
- **Disagreements.** When the repository, the core and a topic file disagree, such as two test
  commands, say what each says and ask which is right before changing either.
- **One command per step.** Record a step as it stands only when it is one command, as rubric
  check 3 defines it: one line calling a named entry point, a runner entry, a script or a tool's
  standard command such as `npm test`, with nothing but `{name}` values, needing no answer from a
  person and exiting non-zero on failure. Check every command you will record in one run before
  writing them, one per line in a quoted heredoc so no quote in a command can break the call:
  `python3 "${CLAUDE_SKILL_DIR}/scripts/one_command.py" <<'EOF'`, the commands, then `EOF`. It
  lists any arguments a command carries of its own; keep them only when the tool's documentation
  gives them as its usual ones, such as `./...` in `go test ./...`.
  The product's own command line, recorded in Running the product as how to reach an interface,
  such as `bin/wordcount --lines {file}`, is the product itself, not a step: record it as it is.
  Anything else, such as flags, settings, folders or accounts the project chose, or several
  commands, goes into a script in the project's scripts folder, with those choices written in. The
  script runs the agreed commands in order and stops at the first failure, passing on any `{name}`
  value the step needs, with no condition, loop, retry or reading of output. Show it to the person
  before writing it. When the project has no scripts folder, create `script/` with the first
  script. When it has a command runner, add an entry that only calls the script and record that
  entry, such as `pnpm check:new-mail`; otherwise record the script, such as `script/check-new-mail`.
  Record only that command and what it is for, never the commands inside the script, since a copy
  in the practice would drift from the script.
  Run a new or changed script only when everything it touches is in the repository or among the
  stand-ins Running the product lists as safe to touch, never a real release, deploy or rollback;
  name each script you did not run, and why, in the hand-over. When a script changes a real
  outside service, the hand-over also suggests, as work for `/agentic:plan`, a test that runs it
  against the stand-in; never write the test or wait for it. A step that needs logic, or a change
  that would add logic to a script, is not yours to write: under the step's heading write "Not set up yet: needs a script with
  logic, work for `/agentic:plan`", so a skill that runs it stops, and give the agreed steps
  in the hand-over, not the practice, as that work. Once the project has a place for
  commands, Check your work names it.

Write only the core, the files under `docs/practices/`, the scripts and runner entries that One
command per step lets you write, and the pull request template above. Leave the rest of
`AGENTS.md` unchanged, creating the file if the project has none, and touch no other file but
`CLAUDE.md`'s import line. Never commit: the person looks at the change and commits it.

## Review

The changed files are reviewed once, corrected once, and then the corrections are checked. The
sequence is fixed so it always ends with a clear result: further rounds of review find little more,
and each round of corrections brings new mistakes. The files of one run are reviewed together,
since the core and a topic file must agree.

1. **Review.** When the files are written, start two agents in the foreground, not in the
   background, both in one message so they run side by side: the `agentic:practices-reviewer` agent
   and the `agentic:language-checker` agent, which checks the wording. Give each this request, its
   first line exactly as shown, naming `AGENTS.md` and each topic file this run changed, separated
   by commas, since a plugin hook reads that line to keep a copy of the files as reviewed:

   ```
   Document: <AGENTS.md's full path>, <each topic file's full path>
   Review these practices. Of AGENTS.md, check only its ## Practices section.
   ```

   Give the document's full path on the `Document:` line, the one you wrote it to: the hook works
   out the document's repository from it, so the review reads the right one whatever folder you
   started in. If it refuses to start them, do what its reason says.
   Each reads everything else it needs itself. Wait for both reports before touching the files.
   If both pass with nothing under Needs a person, go straight to handing over.
2. **Correct, once.** Read the rubric and the Plain words rule again, then correct only what the
   reports list: each failed check and each item under Other findings in the review report, and
   each finding in the wording report. Skip any finding outside the Practices section of
   `AGENTS.md`, which is the person's. A command outside this run's topic that breaks the
   one-command rule stays as written for the person to decide, since writing its script needs them. A wording item under Needs a person, whose meaning only the
   person knows, is a decision like any other. Correct by making the practices accurate, never by
   dropping or hedging what the person said. A finding only the person can settle, such as a rule
   they asked for word for word, or anything under Needs a person, stays as written for them to
   decide. Leave suggestions alone and change nothing else, since an edit beyond the reports is
   the likeliest way to break something. Wait until every edit has succeeded. If nothing in the
   reports was yours to correct, there is nothing to check: go straight to handing over.
3. **Check the corrections.** Start the `agentic:correction-checker` agent in the foreground with
   this request, its first line the same as the review's, and add nothing to it: the hook attaches
   both reports and the files as reviewed, word for word.

   ```
   Document: <AGENTS.md's full path>, <each topic file's full path>
   Check the corrections.
   ```

   If the hook refuses to start it, do what its reason says. If the check fails, stop: change the
   files no further, and show the person the check's report. Do not review or correct again; what
   happens next is their call.

After the sequence, edit the practices only when the person asks. While you are walking through
questions with the person, do not review after each answer: run the sequence once when the
walk-through ends, either because no questions are left or because the person stops. A change the
person makes or asks for at any other time is reviewed once it is made.

Whether the check passed or failed, end with the hand-over. Show the person each document you wrote
or changed: if the app you run in can show them a file in a viewer, use it, and show a fresh copy
after each change if what it shows is a copy; always name each one's full path; never send them to a
code-hosting site to read it. Give the person the files you changed, the review and wording reports
and the check's report, if there was one. Then say how many items they must settle, such as a
finding left for them or a correction the check found not made or broken, and ask the first only, as
a single question; if the person has said not to ask now, ask nothing. List the reviewers'
suggestions separately, as optional. Leave committing to them.
