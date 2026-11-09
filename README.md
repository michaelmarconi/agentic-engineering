# Software Development Lifecycle (SDLC)

A software development lifecycle for [Claude Code](https://code.claude.com/docs), Anthropic's
coding assistant. It takes each piece of work from an idea to reviewed, working code along one
defined path, and keeps what was decided, and why, in a few short Markdown documents in your
repository.

Every document Claude writes is checked by an independent reviewer before you see it, and no
document moves forward until you sign it off. The result is a project whose intent, decisions and
built work can be read from its documents, not lost in old conversations.

## Requirements

- Claude Code, tested on Opus 5.5. Other models may work but are untested.
- Python 3.7 or later, which the plugin's checks run on. On Python 3.6, the plugin warns you
  when a session starts.
- Git, with a remote named `origin`, for [`/build`](docs/skills/build.md), which pushes the branch
  it builds.

## Install

In Claude Code:

```
/plugin marketplace add michaelmarconi/sdlc
/plugin install sdlc@sdlc
```

Or from a terminal:

```bash
claude plugin marketplace add michaelmarconi/sdlc
claude plugin install sdlc@sdlc
```

Install the plugin before you start the session you will use it in: a plugin installed partway
through a session only loads in the next one.

Add `--scope project` to the `install` command to install the plugin for everyone working in a
repository. This records it in the repository's `.claude/settings.json`.

## Quick start

In your repository, run the skills in order. Each one drafts a document with you, has it
reviewed, corrects it and shows you the result to sign off.

1. `/sdlc:brief` writes the product brief: what the product is, who it is for and why.
2. `/sdlc:spec` writes the spec for one capability: what it should do, and how you will know it
   does.
3. `/sdlc:spike` settles any unknown the spec or a decision can't settle without trying
   something, with a throwaway experiment. Skip it when nothing is unknown.
4. `/sdlc:adr` records any technical decision the spec needs.
5. `/sdlc:plan` plans a piece of work against the spec and its decisions.
6. `/sdlc:build` builds the plan on a branch, tests first, and has the result reviewed. Start it
   in a fresh session, or after `/clear`.

You can also ask in your own words, such as "write a spec for invoice reminders". Claude picks
the matching skill.

## How it works

The lifecycle keeps five kinds of document:

| Document | Where | What it holds |
|---|---|---|
| Brief | `docs/brief.md` | What the product is, who it is for and why. One per product. |
| Spec | `docs/specs/` | What one capability should do, and how we will know it does. |
| ADR (architecture decision record) | `docs/adrs/` | One technical decision and why it was made, written to read plain first. |
| Plan | `docs/plans/` | One piece of work that builds part of a spec or an ADR, kept once built as the record of what was built. |
| Spike record | `docs/spikes/` | One hypothesis tested by a throwaway experiment: the experiment, what it produced and the finding, written to read plain first. |

Each document except the brief has a status, such as `📝 Draft` or `🟢 Ready to build`. A
project can also record its **practices**, such as how it is built, tested and released, in
`AGENTS.md` and `docs/practices/`, for Claude and other coding tools to follow.

The plugin works through three parts:

- **Skills:** the steps above, each run as a `/sdlc:<name>` command.
- **Reviewer agents:** separate Claude instances that check each document, each build, or, for
  `/sdlc:audit`, the code against each document, with no memory of your conversation, so the
  conversation cannot sway their judgement. They always run on Sonnet, so the same document gets
  the same judgement whatever model you use.
- **Hooks:** small checks Claude Code runs automatically. They give Claude the lifecycle rules at
  the start of every session in a repository that has a brief or a spec, and refuse any status
  change the lifecycle does not allow.

[The lifecycle rules](docs/lifecycle.md) describe all of it in full. Read them before you edit
documents by hand.

## Skills

| Skill | What it does |
|---|---|
| [`/sdlc:brief`](docs/skills/brief.md) | Writes or changes the product brief |
| [`/sdlc:spec`](docs/skills/spec.md) | Writes or changes the spec for one capability |
| [`/sdlc:spike`](docs/skills/spike.md) | Settles one unknown with a throwaway experiment |
| [`/sdlc:adr`](docs/skills/adr.md) | Records one technical decision |
| [`/sdlc:plan`](docs/skills/plan.md) | Plans a piece of work against its specs and ADRs |
| [`/sdlc:build`](docs/skills/build.md) | Builds a plan on a branch, has it reviewed and hands it back |
| [`/sdlc:practices`](docs/skills/practices.md) | Records how the project does things, one topic at a time |
| [`/sdlc:audit`](docs/skills/audit.md) | Finds where the code and its documents no longer agree, and changes nothing |
| [`/sdlc:feedback`](docs/skills/feedback.md) | Drafts a GitHub issue about the plugin itself |

```mermaid
flowchart LR
    Brief --> Spec
    Spec -->|unknowns| Spike
    Spike -->|facts| Spec
    Spike -->|choices| ADR
    Spec -->|decisions| ADR
    Spec --> Plan
    ADR --> Plan
    Plan --> Build
    Build --> Branch[A reviewed branch]
    Branch -->|you merge| Code[Code on the main branch]
```

## What it changes in your repository

- It writes only the documents above, and the practices you ask it to record, and only when you
  run a skill or ask for one.
- `/sdlc:build` commits to a branch of its own and pushes it. It never commits to the main
  branch, never opens a pull request and never merges: those steps stay with you.
- Review reports are kept in the plugin's own data folder, outside your repository.
- Nothing else is added, unless you install the plugin with `--scope project`.

## Update

```bash
claude plugin marketplace update sdlc
claude plugin update sdlc@sdlc
```

To update automatically, run `/plugin`, open **Marketplaces**, select `sdlc` and choose
**Enable auto-update**. New versions load in the next session, or after `/reload-plugins`.

Read [CHANGELOG.md](CHANGELOG.md) before you update. If a version needs changes to your
documents, its entry says what they are.

## Feedback

Run `/sdlc:feedback` to report a bug or suggest an improvement. It drafts a GitHub issue that
quotes nothing from your repository, shows it to you, and files it only when you agree. You can
also [open an issue](https://github.com/michaelmarconi/sdlc/issues) directly.

## Contributing

Feedback comes in through `/sdlc:feedback` or an issue; pull requests are not accepted from
outside the project. [CONTRIBUTING.md](CONTRIBUTING.md) says why, and where the rules for
working on the plugin live.

## Licence

Released under the [MIT licence](LICENSE).
