# `/practices`

*Not built yet. This page describes the design so far.*

`/practices` is the skill for recording how your project does things, so that a coding agent
building it works the way your team does: the commands it uses to check its work, the rules it
follows, and where to find the detail. It is one step of [the SDLC](../../README.md); read that
page first for the documents, skills and agents it mentions.

## What practices are

Practices are the facts and habits an agent needs to work on the project without asking: how to
set it up and run its tests, how branches and commits are named, what must pass before work is
merged, how it is released. They are the same for every piece of work, so they are written down
once rather than in each plan.

Practices are written for coding agents, such as Claude. Your README, contributing guide and other
documents for people stay yours: `/practices` may read them to learn how you work, but never
changes them.

A choice between real alternatives, such as which language, test framework or library to use, is
not a practice: it is a technical decision, so it belongs in an [ADR](adr.md) (architecture
decision record), where its reasons are kept and only you accept it. The practice then just says
how to use what was chosen, such as the command that runs the tests.

Like the brief, practices have no status. They are never built, only kept true, and edited in
place when the way you work changes. Git is their history.

## Where they live

Practices come in two layers, so an agent always has the essentials but reads the detail only
when its task needs it. Every major coding tool works this way.[^tools]

- **The core**: a `## Practices` section in the project instructions Claude Code loads at the start
  of every session. That is `CLAUDE.md`, or `AGENTS.md` when there is no `CLAUDE.md` or when
  `CLAUDE.md` imports it.[^memory] `AGENTS.md` is a shared format that many coding tools read.[^agentsmd]
  The section is at most 50 lines, since everything in that file takes some of the agent's
  attention on every task and Anthropic advises keeping the whole file under 200
  lines.[^short] It has three parts:
  - **Check your work**: the exact commands for setting up, running every test, running one test
    file, and running the linters and type checker. Anthropic calls the command that checks the
    work "the single most useful line" in these instructions.[^check]
  - **Rules**: short lines the agent must follow, such as "write a failing test before the code
    it tests" or "never edit the files under `src/generated/`".
  - **Read before you**: one line for each topic file below, saying when to read it, such as
    "write or change tests: `docs/practices/testing.md`". A file that is only named is read when
    the agent decides it needs it, so each line says when that is.[^memory]
- **Topic files**: `docs/practices/<topic>.md`, one for each topic with more to say than a line or
  two, such as testing, database changes or releasing. Each is at most 200 lines and points to no
  further files, so the agent never has to follow a chain.

The section and the topic files never import other files. An import loads the whole file into
every session, and a file you don't control, such as the README, can grow without limit.

An example of the core, for a recipe-sharing website built in Python:

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
- Never commit to `main`; work on a branch named `<type>/<short-description>`.
- Never edit files under `src/generated/`; run `uv run make-schema` instead.

### Read before you
- write or change tests: `docs/practices/testing.md`
- release or deploy: `docs/practices/releasing.md`
```

## Using `/practices`

Run `/practices` when you set a project up, again after the first build, and whenever the way you
work changes.

- **Works through a fixed list of topics.** The plugin decides what to ask about, so nothing is
  forgotten: testing, branches and commits, reviews and merging, releasing, and the rest. The
  answers are yours. If you have no view on a topic, it offers the common choice and says it is a
  default.
- **Starts from the repository.** Much of it is already there: build files, test setup,
  continuous integration settings, your README. `/practices` reads them first and proposes what it
  finds, so you confirm rather than dictate. Anything it cannot find, or is not sure of, it asks.
- **One question at a time.** It tells you how many questions it has, then asks them one at a
  time.
- **Hands choices to `/adr`.** When a question turns out to be a choice between alternatives, it
  says so and leaves it for `/adr`, as `/plan` does.
- **Touches only its own parts.** It writes only the `## Practices` section and the files under
  `docs/practices/`, and leaves the rest of the instructions file alone. If the project has
  neither `CLAUDE.md` nor `AGENTS.md`, it creates `CLAUDE.md`. It never commits: you look at the
  change and commit it.

On a new, empty repository there are no commands to find yet, so the first run records your
team's habits, such as test-first working and how branches are named. Run `/practices` again after
the first build, and it proposes the commands the build set up.

`/build` uses your practices but never changes them. It looks for the `## Practices` heading, and
if it is missing, suggests running `/practices` first (see [`/build`](build.md)).

## Review

Before you see the changes, `/practices` has its reviewer agent check them against a short list of
pass-or-fail checks: the section keeps its three parts, every "read before you" line says when to
read its file, each command matches what the repository holds, no secret is written down, and no
choice between alternatives is made there instead of in an ADR. A script checks the sizes: the
section at most 50 lines, each topic file at most 200, and no imports. At the same time, the
language checker reads the changes for words a newcomer could not follow, by the
[Plain words](../lifecycle.md#plain-words) rule. `/practices` corrects what both find, once, and
has the corrections checked (see [Review process](../lifecycle.md#review-process)); then you get
the changes with the reports.

[^tools]: Claude Code loads `CLAUDE.md` always and skills and path-scoped rules only when needed
    ([memory](https://code.claude.com/docs/en/memory)); Cursor has rules that always apply and
    rules attached by file or description, each "under 500 lines"
    ([project rules](https://docs.cursor.com/context/rules)); GitHub Copilot splits instructions
    into focused files of "about 1,000 lines" at most
    ([customize code review](https://docs.github.com/en/copilot/tutorials/customize-code-review));
    Kiro keeps "one domain per file" ([steering](https://kiro.dev/docs/steering/index)).
[^memory]: Claude Code documentation, [How Claude remembers your project](https://code.claude.com/docs/en/memory).
[^agentsmd]: [AGENTS.md](https://agents.md/).
[^short]: Claude Code documentation, [Best practices: keep CLAUDE.md short](https://code.claude.com/docs/en/best-practices#keep-claudemd-short).
[^check]: Claude Code documentation, [Best practices: give Claude a check to run](https://code.claude.com/docs/en/best-practices#give-claude-a-check-to-run).
