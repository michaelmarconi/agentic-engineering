---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: Accepted 👍
date: 2026-11-17
supersedes: 0032
---

# Treat the whole repository as one project, wherever the session starts

## Question

Which folder does each of the plugin's hooks[^hook] treat as the project whose lifecycle[^lifecycle]
documents it checks, including in a repository that holds several apps or packages?

## Decision

Chosen: the top of the git repository is the project, with one `docs/` folder there, wherever in
the repository the session[^session] starts. Every hook finds it through one piece of code all
hooks share:

- A hook that acts on a file goes up from that file to the nearest folder holding git's `.git`.
- A hook that acts on no file, such as the one that gives Claude the lifecycle rules, uses the top
  of the repository holding the session folder. When the session folder is in no repository, as in
  a Claude project thread[^thread], it looks in the session folder and each repository directly
  inside it.

This is chosen because a monorepo[^monorepo] is a single body of work whose parts change together,
so its decisions, planned work and releases belong to the whole repository, not to one app inside
it, and because the place of a file on disk then decides in every kind of session.

## Background

The decision record [ADR 0032](0032-hook-repository-folder.md)[^adr] had each hook find the
repository by going up from the file it acts on, and had a hook that acts on no file look in the
session folder. A later code correction, recorded in no ADR, added one exception: a session started
in a subfolder, such as `apps/web`, treats that subfolder as the project. In a monorepo whose
documents sit in the root `docs/` folder, such a session gets no lifecycle rules at all, since the
hook that gives them looks only in the subfolder, and Claude may then start a second `docs/` folder
inside the app. This ADR replaces [ADR 0032](0032-hook-repository-folder.md), keeping its rule and closing that gap.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| The top of the repository, found through shared code, wherever the session starts | Chosen | One rule; a monorepo's work crosses apps, so its documents do too |
| The session folder, or a subfolder the session started in | Rejected | Wrong in a project thread, and a session started in one app loses the root documents |
| The folder Claude's shell is in | Rejected | Often still the session folder, and it moves as Claude works |
| Each skill[^skill] tells the hook the repository | Rejected | Nothing would check the folder Claude named |
| The nearest folder above a document that holds a brief[^brief] | Rejected | A brief is optional, so it cannot mark a project |
| A setting that names where each kind of document lives | Rejected | Every skill and hook would have to read stored settings before touching a file |

## Consequences

- Good: a monorepo works with no setup, from a session started anywhere in it.
- Good: one piece of code holds the rule for every hook.
- Bad: a repository of unrelated apps cannot keep a separate lifecycle for each app.
- Bad: every hook that acts on a file walks up the folders each time it runs.

## Out of scope

- A repository of unrelated apps that share nothing but the repository, often called code
  colocation; each app can live in a repository of its own.
- Versioning packages of one repository separately, which the release skill does not do today.
- Which app the verify skill starts or a deploy ships: the project's written rules for how it
  does things, such as its commands for running and deploying, can have a section for each app.
- Grouping specs[^spec] into folders, which the lifecycle already allows.
- A project without git: its files use the session folder.
- Repositories nested more than one level below a session folder that is in no repository.
- Scripts Claude runs itself, which take the folder Claude names, and the hook that checks a
  command's git branch, which uses the command's folder.

## How we'll check

Applies to: any hook that judges where a document sits, or looks for the session's repositories.

1. Inspection: no hook in scope works out the project other than through the shared code.
2. Test: a document under a subfolder's `docs/` is not judged as a lifecycle document when the
   session starts in that subfolder.
3. Test: a session started in a subfolder of a repository whose top holds a brief gets the
   lifecycle rules.
4. Test: unit tests run each hook from a session folder above the repository.
5. Demonstration: an install in a project thread's layout gets the lifecycle rules and the checks
   on status changes.
6. Demonstration: an install in a sample monorepo, with the session started inside one app,
   writes a new spec under the repository's top `docs/`.

## Open questions

- None.

## Technical detail

**The shared code.** One module in `scripts/` gives two functions:

- *The project of a path.* A relative path is first made full against the hook event's `cwd`, the
  folder Claude's shell is in, then the session folder: `CLAUDE_PROJECT_DIR`, or the hook's own
  working folder when that is unset. The function goes up from the path's folder to the first
  folder holding `.git`, as a folder or a file, so worktrees and submodules count, and uses the
  session folder when there is none. It makes no exception for a session started in a subfolder.
- *The folders of the session.* When the session folder is inside a repository, that
  repository's top alone; otherwise the session folder, then each repository directly inside it.

**Each hook.**

- The hooks that check the status field of the plugin's documents, references between documents,
  and the size of the project's recorded working rules for agents judge where a written file sits,
  such as directly in the plans[^plan] folder, relative to the project of that file.
- The hook that starts the review agents for a document finds the repository holding the files
  the request's first line names, rewrites that line to name each file relative to it, and adds a
  second line, `Repository: <the repository's full path>`. It refuses to start the agent, and says
  why, if no named file exists, or if the files sit in different repositories.
- The hook that starts the build's review agents, and records which commit they saw, takes the
  repository from the plan file named on the first line of each reviewer's request.
- The session-start hook gives Claude the lifecycle rules when any of the session's folders has a
  product brief, or a specification document with a lifecycle status.

**The lifecycle rules.** The page of lifecycle rules Claude gets at the start of a session says
that every `docs/` path it names is counted from the top of the repository, so the skills write
there from any folder.

[^hook]: A hook is a script Claude Code runs automatically at set moments, such as before Claude writes a file or starts an agent.
[^lifecycle]: The lifecycle is the plugin's set of documents, such as specs and decision records, and the rules for moving each one from draft to settled.
[^session]: A session is one conversation with Claude Code, started in a folder on the person's machine.
[^thread]: A Claude project thread is one conversation inside a project in the Claude app; its session folder holds each of the project's repositories in a folder of its own.
[^monorepo]: A monorepo is one repository holding several related apps or packages that share code and tooling and change together.
[^adr]: An ADR (architecture decision record) is a short document recording one technical decision, the options weighed and why.
[^skill]: A skill is a set of instructions Claude follows for one step, run as a slash command.
[^brief]: A brief is the plugin's one document saying what the product is, who it is for and why.
[^plan]: A plan is the plugin's document for one piece of work that builds part of a spec or an ADR, from draft to built.
[^spec]: A spec is the plugin's document for what one capability of the product should do, and how we will know it does.
