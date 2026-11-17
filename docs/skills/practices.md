# `/practices`

`/practices` is the skill for recording how your project does things, so that a coding agent
building it works the way your team does: the commands it uses to check its work, the rules it
follows, and where to find more detail. It is part of [the lifecycle](../../README.md) but not one of
its steps: you run it whenever you need it. Read that page first for the documents, skills and
agents it mentions.

## What practices are

Practices are the facts and habits an agent needs to work on the project without asking: how to
set it up, run it and test it, how branches and commits are named, what must pass before work is
merged, how it is released. They are the same for every piece of work, so they are written down
once rather than in each plan. They are grouped by topic, such as testing, security or releasing.

Practices are written for coding agents, such as Claude. Your README, contributing guide and other
documents for people stay yours.

A choice between real alternatives, such as which language, test framework or library to use, is
not a practice: it is a technical decision, so it belongs in an [ADR](adr.md) (architecture
decision record), where its reasons are kept and only you accept it. The practice then just says
how to use what was chosen, such as the command that runs the tests.

Because the agents doing the work follow them, the topics leave out ways of working that exist
for people rather than agents, such as sprint length, estimates or pair programming. What
carries over is how work is split and how big each piece may be: small pieces that each leave the
product usable, sized by what a person can review, since reviewing an agent's work is now the
slow step.[^batches]

Like the brief, practices have no status. They are never built; they are corrected in place
whenever the way you work changes, and git keeps the earlier versions.

## Where they live

Practices are kept in two layers, so an agent always has the essentials but reads the detail only
when its task needs it. Coding tools such as Claude Code, Cursor, GitHub Copilot and Kiro split
their instructions the same way.[^tools]

- **The core**: a `## Practices` section in `AGENTS.md`, a format that many coding tools
  read,[^agentsmd] so your practices serve whichever tool your team uses. Claude Code loads its
  project instructions at the start of every session, so every skill and agent sees the core,
  `/plan` and `/build` included. It reads `AGENTS.md` directly only when there is no `CLAUDE.md`,
  only from version 2.1.277 and not in every kind of session, and a personal `CLAUDE.local.md`
  makes it skip `AGENTS.md`. A `CLAUDE.md` holding the line `@AGENTS.md` imports it in every case,
  as Anthropic suggests for sharing one file between tools,[^memory] so `/practices` makes sure that
  line is there. The core is at most 50 lines. That is
  this plugin's own budget: Claude reads the whole file on every task, and Anthropic advises
  keeping it under 200 lines, since a longer file makes Claude follow it less reliably,[^memory] so
  the core leaves most of that room for whatever else the file holds. It has three parts:
  - **Check your work**: the exact commands for setting up, running the product, running every
    test, running one test file, and running the linters and type checker. When a project has
    tests or linters, Anthropic calls the command that runs them "the single most useful line" in
    these instructions.[^check]
  - **Rules**: short lines the agent must follow, such as "write a failing test before the code
    it tests", "open a pull request for every change" or "never edit the files under
    `src/generated/`".
  - **Files to read before a task**: one line for each topic file below, saying which task calls
    for it, such as "before writing or changing tests: `docs/practices/testing.md`". Claude reads
    a file that is only named when it decides it needs it, so each line says when that is.[^memory]
- **Topic files**: `docs/practices/<topic>.md`, one for each topic with more to say than a line or
  two in the core, such as testing, database changes or releasing. Each is at most 200 lines,
  again this plugin's own budget, the same as Anthropic advises for the whole instructions file.
  A topic file names no further files the agent must read, so it reads at most one topic file for
  a task.

The core and the topic files never import other files. An import loads the whole file into every
session, and a file you don't control, such as the README, can grow without limit.

An example of the core, for a recipe-sharing website built in Python. Any other language works the
same way; only the commands change.

```markdown
## Practices

### Check your work
- Set up: `uv sync`
- Run the website: `uv run fastapi dev src/recipes/main.py`
- All tests: `uv run pytest`
- One test file: `uv run pytest tests/test_recipes.py`
- Lint: `uv run ruff check --fix .`
- Format: `uv run ruff format .`
- Place for commands: the `Makefile`
- Type check: `uv run mypy src`

### Rules
- Write a failing test before the code it tests.
- Run the tests, linter and type checker before every commit.
- Never commit to the default branch; work on a branch named `<type>/<short-description>`.
- Open a pull request for every change; a person merges it.
- Never edit files under `src/generated/`; run `uv run make-schema` instead.

### Files to read before a task
- before writing or changing tests: `docs/practices/testing.md`
- before releasing: `docs/practices/releasing.md`
```

## One command per step

Every step the practices record, such as running the tests or releasing, is one command: one line
that calls a named entry point, needs no answer from you and says by its exit code whether it
worked. Every skill can then run a step the same way and tell whether it passed, and nothing has to
interpret a list of instructions written in prose.[^scripts] A named entry point is a command
runner entry, such as a Make target or a script of `package.json`, a script in the project's
scripts folder, or a tool's standard command, such as `npm test` or `pytest {file}`, given nothing
but the values a skill fills in.

Anything more, such as flags, settings, folder or account names your project chose, or several
commands in a row, goes into a script in your scripts folder, so those choices live in a file that
tests can run rather than in a long line of Markdown. `/practices` writes that script for you: it
runs the agreed commands in order and stops at the first failure. It shows you the script first,
creates a `script/` folder if you have none, and, when you have a runner, adds an entry that calls
the script and records that entry. It runs the script only when that changes nothing real, and says
which scripts it did not run. When a script changes a real outside service, such as a mail account,
it suggests a test that runs the script against a stand-in, as work for [`/plan`](plan.md). A step
that needs real logic, such as a retry or a condition, is ordinary work for [`/plan`](plan.md) and
[`/build`](build.md). No other skill writes commands, so they don't pile up across the repository.

## Releasing and deploying

The release and deploy skills act on real systems, such as a package registry or a live server,
and they never ask how: they run what these two topics record. So these topics are stricter than
the rest. Each has a fixed set of headings, and the items under them must come from you or from
what the repository already shows, never from a default Claude proposed. For example:

```markdown
## What may be released
Only commits merged to main.
## Version and its commit
Semver in package.json; each release is tagged v<version>.
## Publish
npm run release
```

A deploying topic has one section per environment, each saying which releases may go there and
the commands that deploy, check that the product works, and roll back. The check is drafted from
Running the product, when it is recorded.

While recording them, `/practices` tries only what is safe: it reads the current version, runs each
check and runs a publish or deploy in its dry-run mode where there is one. It never publishes,
deploys or rolls back. A small script decides whether each topic is complete, and the release and
deploy skills run the same script before acting, so when something is missing they stop and say
exactly what.

## Topics

These are the topics `/practices` suggests. They are a starting point, not a complete list: any
other topic you ask for is recorded the same way.

| Topic | What it records |
|---|---|
| Setting up | What a fresh copy needs: tools, services, local settings, where secrets live, where the project keeps its commands, and the setup command |
| Checking work | The exact commands for all tests, one test file, lint and format, and type check, and which run before every commit |
| Testing | Whether tests come first, what each change is tested with, coverage, end-to-end tests, test data, and flaky or slow tests |
| Branches and commits | Branch names, commit message style, and how long a branch may live |
| Delivering work | How work is split, how big one plan may be, and what done means beyond the merge checks |
| Reviews and merging | Pull requests or not and the sections every description holds, with a [template](#pull-request-template) on GitHub, who reviews, how work is merged, what must pass first, and whether [`/verify`](verify.md) must run and pass before a build is merged |
| CI/CD | What the pipeline runs and when, which checks are required, and what to do when a run fails |
| <a id="releasing"></a>Releasing | Which code may be released, how the version is set and tied to one commit, and the command that publishes it; [`/release`](#releasing-and-deploying) relies on it |
| <a id="deploying"></a>Deploying | For each environment: which releases may go there, and the commands that deploy, check and roll back; [`/deploy`](#releasing-and-deploying) relies on it |
| Database changes | How they are written and applied, and whether they must be reversible |
| Security and dependencies | What to check before adding a dependency, scanning, updates, and handling a security hole |
| Hands off | Files an agent must never edit, and actions it must never take |
| Documents to keep up to date | Which documents must change with the code |
| <a id="running-the-product"></a>Running the product | How to start and stop the product, reach each of its interfaces, put it in a given starting state, and what is safe to touch; [`/verify`](verify.md) relies on it. Before recording it, `/practices` starts the product with the proposed commands and reaches each interface, correcting and trying again until it runs and you agree |

### Pull request template

When you record Reviews and merging and say the project uses pull requests, `/practices` gives
every pull request description the same sections, so a reviewer can tell at a glance what a pull
request is for: a short Summary in plain words, the plan, specs and ADRs it was built from, what
changes, how it was checked, and optional notes. Each section's comment says which part of the
[`/build`](build.md) report to draw it from. On GitHub, which shows a template to everyone opening
a pull request on its website,[^prtemplate] it shows you the
[default template](../../skills/practices/assets/pull_request_template.md) and writes it to
`.github/pull_request_template.md` only if you say yes. If you already have a template, it leaves
yours alone. Either way, the practice gains a rule that descriptions follow the template, so agents
that open pull requests through their own tools follow it too. With no template, because the
project is not on GitHub or you said no, that rule lists the sections instead.
([ADR 0047](../adrs/0047-practices-pull-request-template.md))

## Using `/practices`

You don't set all your practices up front. You add them one topic at a time, whenever you need
them, and improve them as the project grows: how your team works from the start, testing in more
depth once there is more to test, deployment when there is somewhere to deploy to. A practice can
be recorded before the code it describes exists, such as the test command your test framework
will use.

### How a run goes

- **On its own, `/practices` gives an overview and suggests where to start.** It lists the topics,
  each as recorded, not recorded yet, or different from what the repository shows, such as "tests
  exist, but no test command is recorded". When the practices and the repository disagree, it
  says so and asks you which is right. It then suggests the one topic that matters most now,
  judged from the repository and the plans waiting to be built, and offers to start on it. Say
  yes, pick another or stop there. A topic nothing yet needs, such as deployment before there is
  anything to deploy, is not suggested.
- **`/practices <topic>` goes straight to one topic**, such as `/practices testing`. It covers that
  topic alone and stops, so a run is a short conversation. Run it on the same topic later to
  improve it: it starts from what is recorded and proposes changes.
- **Its topics are suggestions, not a complete list.** The plugin offers the common topics listed
  under [Topics](#topics), each with the questions to ask and the choices most teams make. Any other topic works the same way: ask for one, such as "I want
  to define how decisions are approved", and `/practices` gives it a topic file and a line in the
  core. It says so as it
  goes: the overview ends by inviting a topic of your own, and within a topic it asks whether
  there is anything else you want recorded.
- **Reads the repository first.** Much of it is already there: build files, test setup,
  continuous integration settings, your README. `/practices` reads them and proposes what it
  finds, so you confirm rather than dictate. Anything it cannot find, or is not sure of, it asks.
- **One question at a time, each with a proposal.** It tells you how many questions it has, then
  asks them one at a time. Each question starts with a short summary of what it is about and what
  the repository shows, so you can answer without knowing the repository, then sets its proposal
  apart in a quote, with the reason, for you to accept, change or reject, and asks the question
  last. Anything you already said, such as answers given
  with the request, is used rather than asked again.
- **Bases its proposals on current advice.** The answers are yours, but when you have no view on a
  question, it asks whether to look up current advice on the web for your language and tools,
  rather than rely on what Claude already knows, which may be out of date. It then proposes a
  default, names the sources it used, and marks the default as one in the practices, by ending
  it with "(default)". If you
  decline, or the session cannot reach the web, it says its proposal comes from Claude's own
  knowledge.

### What it never does

- **Require anything.** Running `/practices` is optional, and so is every topic. A question you
  don't answer is left out, never written as a guess, so it shows as not recorded in the overview.
- **Make a technical choice.** When a question turns out to be a choice between alternatives, it
  says so and leaves it for you to record with `/adr`, as `/plan` does. A command for a tool the
  project does not use yet is marked by ending it with "(not set up yet)".
- **Change anything else.** It writes only the core, the files under `docs/practices/`, any
  script a recorded step needs and the pull request template you agree to, and
  leaves the rest of `AGENTS.md` alone, creating the file if the project has none. In `CLAUDE.md`
  it adds only the `@AGENTS.md` line, creating the file if needed, and asks you first when the file
  already exists. It never touches your README, contributing guide or any other file unless you
  explicitly ask it to.
- **Commit.** You look at the change and commit it.

`/build` follows your practices but never changes them. Where a practice is not recorded, it works
it out from the repository and says what it assumed (see [`/build`](build.md)).
[`/plan`](plan.md) keeps each plan to any size or way of splitting work they record.

## Review

Before you see the changes, `/practices` has its reviewer agent check them against a short list of
pass-or-fail checks, such as: each command matches what the repository holds, no secret is
written down, and no choice between alternatives is made there instead of in an ADR. The core and
any topic file a run changed are reviewed together, since they must agree. A hook, a script Claude
Code runs before every edit, refuses an edit that would take a file past the 50-line or 200-line
limit and make it longer, or add an import, so those never reach the review. Beside the reviewer,
the language checker, an agent shared by every skill that writes a document, reads the changes
for words a newcomer could not follow, by the [Plain words](../lifecycle.md#plain-words) rule.
Both are corrected once, as for
every document (see [Review process](../lifecycle.md#review-process)).

[^tools]: [Claude Code](https://code.claude.com/docs/en/memory), [Cursor](https://docs.cursor.com/context/rules),
    [GitHub Copilot](https://docs.github.com/en/copilot/tutorials/customize-code-review) and
    [Kiro](https://kiro.dev/docs/steering/index) each load a short set of instructions always and
    the rest only when a task calls for it.
[^memory]: Claude Code documentation, [How Claude remembers your project](https://code.claude.com/docs/en/memory).
[^agentsmd]: [AGENTS.md](https://agents.md/).
[^prtemplate]: GitHub Docs, [Creating a pull request template for your repository](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository).
[^check]: Claude Code documentation, [Best practices: give Claude a check to run](https://code.claude.com/docs/en/best-practices#give-claude-a-check-to-run).
[^scripts]: GitHub's [Scripts to Rule Them All](https://github.blog/engineering/scripts-to-rule-them-all/) describes the same idea: one script per task, with the same names in every project.
[^batches]: DORA's research on [working in small batches](https://dora.dev/capabilities/working-in-small-batches/)
    finds that small batches predict better delivery, and matter more when AI writes the code,
    since "large changes are difficult to review, test, and integrate safely".
