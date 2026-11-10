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
recorded, not recorded yet, or out of step with the repository, with a few words on why, such as
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

Use every answer the person has already given, and ask only what remains. When you have
questions, say how many, then ask only the first. Start it with a short summary of what it is
about and what the repository shows, so someone who does not know the repository can answer, and
end it with a proposal they can accept, change or reject; give any examples as possible answers,
not further questions. Ask the next once the first is settled, saying the answer is noted, not
recorded: nothing is recorded until the files are written. If the person has said not to ask,
write what is settled and ask nothing. Otherwise, even when their answers covered everything,
finish the topic by asking whether there is anything else about it they want recorded, in the
hand-over if you have written the files: the topics file is only a starting point, and they know
what it misses. Being asked to ask only what you must does not waive this question; only being
told not to ask anything does.

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
- **Disagreements.** When the repository, the core and a topic file disagree, such as two test
  commands, say what each says and ask which is right before changing either.

Write only the core and the files under `docs/practices/`. Leave the rest of `AGENTS.md`
unchanged, creating the file if the project has none, and touch no other file but `CLAUDE.md`'s
import line. Never commit: the person looks at the change and commits it.

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
   `AGENTS.md`, which is the person's. A wording item under Needs a person, whose meaning only the
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
