# `/practices`

*Not built yet. This page describes the design so far.*

`/practices` is the skill for recording how your project does things: how to set it up, build,
test, run and release it, and what your team expects before work is merged. It is one step of
[the SDLC](../../README.md); read that page first for the documents, skills and agents it
mentions.

## What practices are

Practices are the facts and habits someone needs to work on the project without asking: the
commands, the machine it needs, and the team's rules for branches, commits and reviews. They are
the same for every piece of work, so they are written down once, when you set the project up,
rather than in each plan.

Practices are not a document of the lifecycle. They live where Claude Code already looks for
project instructions, so every session and every agent that loads those instructions sees them,
whether or not a skill is running. That is `CLAUDE.md`, or `AGENTS.md` when there is no
`CLAUDE.md` or when `CLAUDE.md` imports it.[^memory] Your practices sit under a `## Practices`
heading there, beside anything else the file holds.

Like the brief, practices have no status. They are never built, only kept true, and edited in
place when the way you work changes. Git is their history.

## What they cover

| Practice | Holds |
|---|---|
| Setting up | How to get a fresh copy of the project ready to work on |
| Building, testing and running | The command for each, and the linters that must pass |
| Releasing and deploying | How a change reaches its users |
| Machine | Any operating system or hardware the work needs, such as a Mac to build an iPhone app |
| Configuration and secrets | Where they live, and how to get them; never the secrets themselves |
| Branches and commits | How they are named and written |
| Reviews and merging | Whether you use pull requests, who reviews, and what must pass before work is merged |

A choice between real alternatives, such as which test framework or library to use, or how errors
are handled, is not a practice: it is a technical decision, so it belongs in an
[ADR](adr.md) (architecture decision record), where its reasons are kept and only you accept it.
The practice then just says how to use what was chosen, such as the command that runs the tests.

## Using `/practices`

Run `/practices` when you set a project up, or whenever the way you work changes.

- **Starts from the repository.** Unlike the brief, which records what only you intend, practices
  are mostly facts the repository already shows: its build files, its test setup, its continuous
  integration settings. `/practices` reads them first and proposes what it finds, so you confirm
  rather than dictate. Anything it cannot find, or is not sure of, it asks.
- **One question at a time.** It tells you how many questions it has, then asks them one at a
  time.
- **Hands choices to `/adr`.** When a question turns out to be a choice between alternatives, it
  says so and leaves it for `/adr`, as `/plan` does.
- **Touches only its own section.** It writes under the `## Practices` heading and changes nothing
  else in the file. If the project has neither file, it creates `CLAUDE.md`. It never commits:
  you look at the change and commit it.

`/build` uses your practices but never changes them. If they are missing, it suggests running
`/practices` first (see [`/build`](build.md)).

## Review

Before you see the practices, `/practices` has its reviewer agent check them against a short list
of pass-or-fail checks: each practice says something someone could act on, each command matches
what the repository holds, no secret is written down, and no choice between alternatives is made
there instead of in an ADR. At the same time, the language checker reads them for words a
newcomer could not follow, by the [Plain words](../lifecycle.md#plain-words) rule. `/practices`
corrects what both find, once, and has the corrections checked (see
[Review process](../lifecycle.md#review-process)); then you get the practices with the reports.

[^memory]: Claude Code documentation, [How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md),
    which also advises keeping these files to what Claude should know in every session:
    "build commands, conventions, project layout, 'always do X' rules".
