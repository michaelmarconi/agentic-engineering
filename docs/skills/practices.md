# `/practices`

*Not built yet. This page describes the design so far.*

`/practices` is the skill for recording how your project does things, so that a coding agent
building it works the way your team does: the commands it uses to check its work, the rules it
follows, and where to find more detail. It is one step of [the SDLC](../../README.md); read that
page first for the documents, skills and agents it mentions.

## What practices are

Practices are the facts and habits an agent needs to work on the project without asking: how to
set it up and run its tests, how branches and commits are named, what must pass before work is
merged, how it is released. They are the same for every piece of work, so they are written down
once rather than in each plan. They are grouped by topic, such as testing, security or releasing.

Practices are written for coding agents, such as Claude. Your README, contributing guide and other
documents for people stay yours: `/practices` may read them to learn how you work, but never
changes them.

A choice between real alternatives, such as which language, test framework or library to use, is
not a practice: it is a technical decision, so it belongs in an [ADR](adr.md) (architecture
decision record), where its reasons are kept and only you accept it. The practice then just says
how to use what was chosen, such as the command that runs the tests.

Like the brief, practices have no status. They are never built; they are corrected in place
whenever the way you work changes, and git keeps the earlier versions.

## Where they live

Practices are kept in two layers, so an agent always has the essentials but reads the detail only
when its task needs it. Several coding tools split their instructions the same way.[^tools]

- **The core**: a `## Practices` section in the project instructions that Claude Code loads at the
  start of every session. That is `CLAUDE.md`, or `AGENTS.md` when there is no `CLAUDE.md` or when
  `CLAUDE.md` imports it; if both exist and `CLAUDE.md` does not import `AGENTS.md`, Claude Code
  reads only `CLAUDE.md`, so the section goes there.[^memory] `AGENTS.md` is a format that many
  coding tools read;[^agentsmd] other tools may not read `CLAUDE.md`. The section is at most 50
  lines, a limit this plugin sets: Claude reads the whole file on every task, and Anthropic advises
  keeping it under 200 lines, since a longer file makes Claude follow it less reliably.[^memory]
  It has three parts:
  - **Check your work**: the exact commands for setting up, running every test, running one test
    file, and running the linters and type checker. When a project has tests or linters,
    Anthropic calls the command that runs them "the single most useful line" in these
    instructions.[^check]
  - **Rules**: short lines the agent must follow, such as "write a failing test before the code
    it tests" or "never edit the files under `src/generated/`".
  - **Files to read before a task**: one line for each topic file below, saying which task calls
    for it, such as "before writing or changing tests: `docs/practices/testing.md`". Claude reads
    a file that is only named when it decides it needs it, so each line says when that is.[^memory]
- **Topic files**: `docs/practices/<topic>.md`, one for each topic with more to say than a line or
  two, such as testing, database changes or releasing. Each is at most 200 lines, again this
  plugin's limit, and names no further files the agent must read, so it never has to go more than
  one file deep.

The section and the topic files never import other files. An import loads the whole file into
every session, and a file you don't control, such as the README, can grow without limit.

An example of the core, for a recipe-sharing website built in Python. Any other language works the
same way; only the commands change.

```markdown
## Practices

### Check your work
- Set up: `uv sync`
- All tests: `uv run pytest`
- One test file: `uv run pytest tests/test_recipes.py`
- Lint and format: `uv run ruff check --fix . && uv run ruff format .`
- Type check: `uv run mypy src`

### Rules
- Write a failing test before the code it tests.
- Run the tests, linter and type checker before every commit.
- Never commit to the default branch; work on a branch named `<type>/<short-description>`.
- Never edit files under `src/generated/`; run `uv run make-schema` instead.

### Files to read before a task
- before writing or changing tests: `docs/practices/testing.md`
- before releasing or deploying: `docs/practices/releasing.md`
```

## Using `/practices`

You don't set all your practices up front. You add them one topic at a time, whenever you need
them, and improve them as the project grows: how your team works from the start, testing in more
depth once there is more to test, deployment when there is somewhere to deploy to. A practice can
be recorded before the code it describes exists, such as the test command your test framework
will use. Whenever the repository and the practices disagree, the overview says so.

- **On its own, `/practices` gives an overview and suggests where to start.** It lists the topics,
  each as recorded, not recorded yet, or different from what the repository shows, such as "tests
  exist, but no test command is recorded". It then suggests the one topic that matters most now,
  judged from the repository and the plans waiting to be built, and offers to start on it. Say
  yes, pick another or stop there. A topic nothing yet needs, such as deployment before there is
  anything to deploy, is not suggested.
- **`/practices <topic>` goes straight to one topic**, such as `/practices testing`. It covers that
  topic alone and stops, so a run is a short conversation, not a long interview. Run it on the
  same topic later to improve it: it starts from what is recorded and proposes changes.
- **Its topics are suggestions, not a complete list.** The plugin offers common topics, such as
  testing, security and releasing, each with the questions to ask and the choices most teams
  make, so you can start from what usually works. Any other topic works the same way: ask for
  one, such as "I want to define how decisions are approved", and `/practices` gives it a topic
  file and a line in the core, like any other. The skill says so as it goes: the overview ends by
  inviting a topic of your own, and within a topic it asks whether there is anything else you want
  recorded, so you are never limited to its questions.
- **Nothing is required.** Running `/practices` is optional, and so is every topic. A question you
  don't answer is left out, never written as a guess, so it shows as not recorded in the overview.
- **Suggests a default when you have no view, from current advice.** The answers are yours. If you
  have no view on a question, it offers to look up current advice on the web, for your language
  and tools, rather than rely on what Claude already knows, which may be out of date. It then
  suggests a default, names the sources it used, and marks the default as one in the practices. If
  you decline, or the session cannot reach the web, it says its suggestion comes from Claude's own
  knowledge.
- **Reads the repository first.** Much of it is already there: build files, test setup,
  continuous integration settings, your README. `/practices` reads them and proposes what it
  finds, so you confirm rather than dictate. Anything it cannot find, or is not sure of, it asks.
- **One question at a time.** It tells you how many questions it has, then asks them one at a
  time.
- **Leaves choices to `/adr`.** When a question turns out to be a choice between alternatives, it
  says so and leaves it for you to record with `/adr`, as `/plan` does.
- **Changes only the practices.** It writes only the `## Practices` section and the files under
  `docs/practices/`, and leaves the rest of the instructions file alone. If the project has
  neither `CLAUDE.md` nor `AGENTS.md`, it creates `CLAUDE.md`. It never commits: you look at the
  change and commit it.

`/build` follows your practices but never changes them. Where a practice is not recorded, it works
it out from the repository and says what it assumed (see [`/build`](build.md)).

## Review

Before you see the changes, `/practices` has its reviewer agent check them against a short list of
pass-or-fail checks, such as: each command matches what the repository holds, no secret is
written down, and no choice between alternatives is made there instead of in an ADR. A script
checks this plugin's size limits and that nothing is imported. At the same time, the language
checker, an agent shared by every skill, reads the changes for words a newcomer could not follow,
by the [Plain words](../lifecycle.md#plain-words) rule. Both are corrected once, as for every
document (see [Review process](../lifecycle.md#review-process)).

[^tools]: Claude Code loads `CLAUDE.md` always and skills and path-scoped rules only when needed
    ([memory](https://code.claude.com/docs/en/memory)); Cursor has rules that always apply and
    rules attached by file or description, each "under 500 lines"
    ([project rules](https://docs.cursor.com/context/rules)); GitHub Copilot's code review splits
    instructions into focused files of "about 1,000 lines" at most
    ([customize code review](https://docs.github.com/en/copilot/tutorials/customize-code-review));
    Kiro keeps "one domain per file" ([steering](https://kiro.dev/docs/steering/index)).
[^memory]: Claude Code documentation, [How Claude remembers your project](https://code.claude.com/docs/en/memory).
[^agentsmd]: [AGENTS.md](https://agents.md/).
[^check]: Claude Code documentation, [Best practices: give Claude a check to run](https://code.claude.com/docs/en/best-practices#give-claude-a-check-to-run).
