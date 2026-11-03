# `/practices`

*Not built yet. This page describes the design so far.*

`/practices` is the skill for recording how your project does things: how to set it up, build,
test, run and release it, and what your team expects before work is merged. It is one step of
[the SDLC](../../README.md); read that page first for the documents, skills and agents it
mentions.

## What practices are

Practices are the facts and habits someone needs to work on the project without asking: the
commands, the machine it needs, and the team's rules for branches, commits and reviews. They are
the same for every piece of work, so they are written down once rather than in each plan.

Practices are not a new kind of document. They live in the files that projects already keep for
this, and each fact is written once, for people. Agents are pointed to it rather than given a copy,
so the two can never disagree.

| File | Who it is for | Practices it holds |
|---|---|---|
| `README.md` | Anyone arriving at the project | Setting up, building, testing, running, releasing and deploying; any operating system or hardware the work needs; where configuration and secrets live, never the secrets themselves |
| `CONTRIBUTING.md` | Anyone changing the project | How branches and commits are named; pull requests and review; what must pass before work is merged |
| `AGENTS.md`, or `CLAUDE.md` | Coding agents, such as Claude | A short `## Practices` section that points to the two files above, and anything only an agent needs, such as "run the linter before every commit" |

This follows the files' usual roles. GitHub shows the README on a project's front page and links to
`CONTRIBUTING.md` when someone opens an issue or pull request.[^contributing] `AGENTS.md` is a
shared format read by many coding tools, which keeps READMEs "focused on human
contributors";[^agentsmd] `CLAUDE.md` is Claude Code's own version. Claude Code reads `CLAUDE.md`,
or `AGENTS.md` when there is no `CLAUDE.md` or when `CLAUDE.md` imports it, and `/practices` writes
the section into whichever of the two Claude Code loads.[^memory]

The `## Practices` section imports a short file, with a line such as `@CONTRIBUTING.md`, so its
whole text loads into every session. A long file it only names, written in backticks, so Claude
opens it when needed: an imported file costs room in every session, and Anthropic advises keeping
these instructions short.[^memory]

A choice between real alternatives, such as which language, test framework or library to use, is
not a practice: it is a technical decision, so it belongs in an [ADR](adr.md) (architecture
decision record), where its reasons are kept and only you accept it. The practice then just says
how to use what was chosen, such as the command that runs the tests.

Like the brief, practices have no status. They are never built, only kept true, and edited in
place when the way you work changes. Git is their history.

## Using `/practices`

Run `/practices` when you set a project up, again after the first build, and whenever the way you
work changes.

- **Starts from the repository.** Practices are mostly facts the repository already shows: its
  build files, its test setup, its continuous integration settings. `/practices` reads them first
  and proposes what it finds, so you confirm rather than dictate. Anything it cannot find, or is
  not sure of, it asks.
- **One question at a time.** It tells you how many questions it has, then asks them one at a
  time.
- **Hands choices to `/adr`.** When a question turns out to be a choice between alternatives, it
  says so and leaves it for `/adr`, as `/plan` does.
- **Touches only its own parts.** It changes only the sections it writes in each file and leaves
  the rest alone, creating a file only when the project has none. It never commits: you look at
  the change and commit it.

`/build` uses your practices but never changes them. It looks for the `## Practices` heading, and
if it is missing, suggests running `/practices` first (see [`/build`](build.md)).

## An example

A new project holds only `docs/brief.md`, for a recipe-sharing website, and one spec. There is no
code yet.

1. You run `/practices`. With nothing but the documents to read, it asks how you work: whether
   you use pull requests and who reviews them, how branches and commits are named, what must pass
   before merging, and where the website will run. It writes your answers to `CONTRIBUTING.md`,
   and creates `CLAUDE.md` with a `## Practices` section that imports it.
2. Asked which language and test framework to use, it says those are choices, so you record them
   with `/adr`: Python with FastAPI, and pytest.
3. You run `/plan`, then `/build`. The first build writes the code and the test setup, following
   those ADRs and `CONTRIBUTING.md`.
4. You run `/practices` again. The repository now has a build file, so it proposes the commands to
   set up, test and run the website. You confirm them, and it writes them to the README and points
   the `## Practices` section at it.

On an empty repository, then, practices start as the team's habits, and the commands follow the
first build.

## Review

Before you see the changes, `/practices` has its reviewer agent check them against a short list of
pass-or-fail checks: each practice says something someone could act on, each command matches what
the repository holds, no secret is written down, no fact is written in two places, and no choice
between alternatives is made there instead of in an ADR. At the same time, the language checker
reads them for words a newcomer could not follow, by the [Plain words](../lifecycle.md#plain-words)
rule. `/practices` corrects what both find, once, and has the corrections checked (see
[Review process](../lifecycle.md#review-process)); then you get the changes with the reports.

[^contributing]: GitHub documentation, [Setting guidelines for repository contributors](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors).
[^agentsmd]: [AGENTS.md](https://agents.md/): "README.md files are for humans", while
    `AGENTS.md` holds "the extra, sometimes detailed context coding agents need".
[^memory]: Claude Code documentation, [How Claude remembers your project](https://code.claude.com/docs/en/memory),
    which shows a `CLAUDE.md` pointing to the README with "See @README for project overview", and
    advises keeping these files under 200 lines, since "longer files consume more context and
    reduce adherence".
