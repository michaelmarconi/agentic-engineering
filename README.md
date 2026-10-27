# Software Development Lifecycle (SDLC)

*In development: `/brief`, `/spec`, `/adr` and `/issue` are built; the other skills are still being designed.*

A software development lifecycle is the path work takes from an idea for a product to working
code. This repository defines one, and packages it as a plugin for
[Claude Code](https://code.claude.com/docs), Anthropic's coding assistant, so that Claude follows
it with you in any repository you install it in.

## Install

Tested with Claude Code on Sonnet 5.5 and Opus 5.5 (see [Models](#models)).

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

Add `--scope project` to the `install` command to share the plugin with everyone working in a
repository.

### Update

```bash
claude plugin marketplace update sdlc
claude plugin update sdlc@sdlc
```

To update automatically, run `/plugin`, open **Marketplaces**, select `sdlc` and choose
**Enable auto-update**. New versions load on the next session or after `/reload-plugins`.

Claude Code doesn't say what a new version changed, so [CHANGELOG.md](CHANGELOG.md) does. Read
it before you update past a major version, for example from 1.x to 2.0: it says what you need to
change in your documents. Until 1.0, any minor version may need such a change, and its entry
says so.

## How it works

The lifecycle keeps its thinking in a few kinds of document, each a Markdown file in your
repository:

- **Brief:** what the product is, who it is for and why. One per product, holding only what is
  true of the whole product.
- **Spec:** what one capability of the product should do, and how we will know it does. A
  product has many.
- **ADR** (architecture decision record): one technical decision and why it was made. Once
  accepted it is never edited; a later decision supersedes it with a new ADR.
- **Plan:** a piece of work that builds part of a spec or an ADR. It is deleted once built.

Each document except the brief has a status, such as Draft or Ready to build, which says how far
along it is. The brief has none, because it is never built, only kept true.

The plugin gives Claude three kinds of help to work with these documents:

- **Skills:** instructions Claude follows for one step, which you run as a slash command such as
  [`/spec`](docs/skills/spec.md). The plugin's skills are named `/sdlc:spec` and so on; this page leaves out the
  `sdlc:` prefix.
- **Agents:** separate Claude instances that start with no memory of your conversation and
  only the tools they need, so their work is not swayed by your conversation. A skill hands them work such as
  building a plan or reviewing a document.
- **Hooks:** small scripts Claude Code runs automatically at set moments. This plugin uses them
  to give Claude a summary of the lifecycle when a session starts in a repository that uses it,
  and to refuse spec and ADR edits Claude makes that the lifecycle does not allow, such as an illegal
  status change. They need Python 3.

Every document a skill writes is reviewed before you see it (see [Review process](#review-process)). Apart
from the documents, the plugin adds nothing to your repository, unless you choose to install it
for everyone working there (see [Install](#install)).

## Principles

The rules the lifecycle follows, such as one decision per ADR, are kept in one short file,
[context/sdlc.md](context/sdlc.md). The plugin gives that file to Claude at the start of every
session in a repository that has a brief or a spec, so Claude knows how the
steps fit together even when you run only one of them.

## Skills

Each step of the lifecycle has a skill. In the order you would use them:

```mermaid
flowchart TD
    Brief --> Spec
    Spec -->|unknowns| Spike
    Spike -->|facts| Spec
    Spike -->|choices| ADR
    Spec -->|decisions| ADR
    Spec --> Plan
    ADR --> Plan
    Plan --> Build
    Build --> Code[Code on the main branch]
    Code -.-> Audit
    Audit -.->|drift| Spec
```

Planning, from the brief to the plan, decides what to build and how. Building turns a plan into
reviewed code on the main branch. Auditing finds where the code and its documents have drifted
apart.

### [`/brief`](docs/skills/brief.md)

Writes or changes the brief with you, from what you say and the documents you point it to. Every
spec is written against it.

### [`/spec`](docs/skills/spec.md)

Writes or changes a spec with you. Research is part of writing it.

### [`/spike`](docs/skills/spike.md)

*Not built yet.* When an unknown can only be settled by trying something, we build a throwaway
experiment before the real work. A fact goes back into the spec; a choice becomes an ADR. A spike
agent runs the experiment in its own copy of the repository, so the throwaway code never touches
the real work.

### [`/adr`](docs/skills/adr.md)

Records a technical decision with you, whether it came from a spike or straight from shaping a
spec: one decision per ADR, with the options it beat. Only you can accept or reject it.

### [`/plan`](docs/skills/plan.md)

*Not built yet.* Scopes a piece of work against the specs and ADRs it delivers.

### [`/build`](docs/skills/build.md)

*Not built yet.* A build agent carries out the plan, then four reviewer agents check the result
in parallel:

- **Code:** is it correct and well made?
- **Security:** does it open any holes?
- **Spec:** is everything the plan was for built and shown to work, with nothing unrequested
  added? Once every requirement in the spec is, the spec is marked Built.
- **ADRs:** is every accepted decision followed, not just the ones the plan touches?

Findings follow the same [review process](#review-process) as documents: the build agent fixes
them once, then a confirm check asks whether each fix landed and nothing broke. A clean review or
a passing confirm merges the work into the main branch; a failing confirm stops and asks for help.

### [`/audit`](docs/skills/audit.md)

*Not built yet.* Code and its documents can drift apart, for example when someone changes code
without going through this lifecycle. `/audit` runs the spec and ADR reviewers across the whole
repository and reports where they disagree; you choose whether to fix the code, reopen the spec,
or supersede the ADR.

## Review process

Agents don't mark their own homework. The agent that writes a document can miss its own
mistakes, so every document a skill writes is checked by a reviewer agent before you see it.
The reviewer starts fresh, without your conversation, so it judges the page as a newcomer would.
It checks the document against the skill's rubric: a short list of pass-or-fail checks, such as
"each requirement has exactly one rule". The same rubric guides the skill while it writes.

Every review follows the same fixed sequence:

```mermaid
flowchart TD
    Write --> Review
    Review -->|findings| Fix
    Review -->|none| You
    Fix --> Confirm
    Confirm -->|passes| You
    Confirm -->|fails| Stop[Stop and show you]
```

1. **Review.** The reviewer checks the whole document and reports pass or fail for each check.
   For each failure it quotes the check and the words that break it.
2. **Fix.** The skill fixes every finding it can, once. A choice only you can make becomes an
   open question for you, never a guess.
3. **Confirm.** A reviewer checks only that each fix landed and that no edit broke anything.
   Anything else it notices reaches you as a suggestion, not a failure.
4. **You.** You get the document with the reports. If the confirm check failed, the skill stops
   there and shows you why, rather than trying again.

A finding is one of three kinds. A **failure** breaks a check, and the skill fixes it. A
**decision** is something only you can settle, such as which of two readings you meant; it goes
to you as an open question. A **suggestion** is something you might want to add; it never holds
a document back.

There are no repeated rounds of review and fix. We measured this on specs with planted
mistakes: one review finds nearly every one, and each further round of fixes brings new
problems ([results](experiments/review-seeding/RESULTS.md)).

## Models

Claude Code can run on different Claude models, and a skill that works well on one may behave
differently on another. The plugin handles this in three ways.

- **Skills use your model.** A skill (such as `/spec`) runs on whichever model your Claude Code
  session uses, so you choose it, with `/model`, as you normally would.
- **Reviewers use a fixed model.** Each skill hands its work to a reviewer, a separate Claude
  that checks the document against a list of rules and reports what fails. Reviewers always run
  on Sonnet, so the same document gets the same judgement whatever model your session uses. To
  override it, set the environment variable `CLAUDE_CODE_SUBAGENT_MODEL` to a model name together
  with `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (Claude Code 2.1.257 or later); note that this
  changes every subagent, not just the reviewers. Results on other models are untested.
- **Every change is tested on each supported model.** Each skill has evals: scripted
  conversations whose results are checked automatically, some by simple text matching and some by
  a second Claude acting as judge, always Sonnet. A change is released only if its evals pass
  on Sonnet 5.5 and on Opus 5.5, the models listed under [Install](#install). When a new model
  comes out, the evals are run on it before it is added to that list.

## Reporting a problem

### [`/issue`](docs/skills/issue.md)

When a skill gets something wrong, or the lifecycle gets in your way, `/issue` turns it into an
issue on this plugin's GitHub repository. It asks what happened and what you expected, gathers
the versions involved, and leaves out anything that would identify your project. You see the
draft before anything is filed. Each issue becomes a test the plugin must pass before the fix
is released, so the same problem can't quietly come back.

## Contributing

Read [AGENTS.md](AGENTS.md) first. It holds the rules every skill is built to and the checks a
change must pass.
