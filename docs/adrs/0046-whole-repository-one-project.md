---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: 2026-11-17
---

# Treat the whole repository as one project, wherever the session starts

## Question

In a repository that holds several apps or packages, which folder does the plugin treat as the
project whose lifecycle[^lifecycle] documents it reads, writes and checks?

## Decision

Chosen: the whole git repository is one project, with one `docs/` folder at its top, wherever in
the repository the session[^session] starts. So a hook judges every document from the repository's
top, and a hook that acts on no file, such as the one that gives Claude the lifecycle rules, looks
at the top of the repository holding the session folder. A monorepo[^monorepo] is a single body of
work whose parts change together, so its decisions, planned work and releases belong to the whole
repository, not to one app inside it.

## Background

The decision record [ADR 0032](0032-hook-repository-folder.md)[^adr] has each hook[^hook] find
the repository by going up from the file it acts on, and has a hook that acts on no file look in
the session folder. A later code correction, recorded in no ADR, added one exception: a session
started in a subfolder, such as `apps/web`, treats that subfolder as the project. In a monorepo whose documents sit in the root
`docs/` folder, such a session gets no lifecycle rules at all, since the hook that gives them looks
only in the subfolder, and Claude may then start a second `docs/` folder inside the app.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| The whole repository, wherever the session starts | Chosen | One rule; a monorepo's work crosses apps, so its documents do too |
| The folder the session started in, when that is inside the repository | Rejected | A session started in one app loses the root documents and may start new ones there |
| The nearest folder above a document that holds a brief[^brief] | Rejected | A brief is optional, so it cannot mark a project |
| A setting that names where each kind of document lives | Rejected | Every skill[^skill] and hook would have to read stored settings before touching a file |

## Consequences

- Good: a monorepo works with no setup, from a session started anywhere in it.
- Good: every hook judges a document's place by one rule.
- Bad: a repository of unrelated apps cannot keep a separate lifecycle for each app.

## Out of scope

- A repository of unrelated apps that share nothing but the repository, often called code
  colocation; each app can live in a repository of its own.
- Versioning packages of one repository separately, which the release skill does not do today.
- Which app the verify skill starts or a deploy ships: the project's written rules for how it
  does things, such as its commands for running and deploying, can have a section for each app.
- Grouping specs[^spec] into folders, which the lifecycle already allows.
- A file in no repository, and a session folder in no repository, which work as before.

## How we'll check

Applies to: any hook that judges where a document sits, or looks for the session's repositories.

1. Test: a document under a subfolder's `docs/` is not judged as a lifecycle document when the
   session starts in that subfolder.
2. Test: a session started in a subfolder of a repository whose top holds a brief gets the
   lifecycle rules.
3. Demonstration: an install in a sample monorepo, with the session started inside one app,
   writes a new spec under the repository's top `docs/`.

## Open questions

### 1. Does this ADR replace [ADR 0032](0032-hook-repository-folder.md), or sit beside it?

This ADR changes where a hook that acts on no file looks, which
[ADR 0032](0032-hook-repository-folder.md) decides, so the two disagree on that one point.

> **Proposed:** Replace it: this ADR carries over the rest of its rule and gains `supersedes: 0032`.
>
> **Why:** Two Accepted ADRs that disagree would leave a reader unsure which holds.

## Technical detail

**Finding the project.** The shared code in `scripts/repository.py` judges every path from the
top of the git repository holding it, dropping the exception for a session started in a
subfolder.

**The session's folders.** For a hook with no file, when the session folder is inside a
repository, the folder looked in is that repository's top, not the session folder.

**The lifecycle rules.** The page of lifecycle rules Claude gets at the start of a session says
that every `docs/` path it names is counted from the top of the repository, so the skills write
there from any folder.

[^lifecycle]: The lifecycle is the plugin's set of documents, such as specs and decision records, and the rules for moving each one from draft to settled.
[^session]: A session is one conversation with Claude Code, started in a folder on the person's machine.
[^monorepo]: A monorepo is one repository holding several related apps or packages that share code and tooling and change together.
[^adr]: An ADR (architecture decision record) is a short document recording one technical decision, the options weighed and why.
[^hook]: A hook is a script Claude Code runs automatically at set moments, such as before Claude writes a file.
[^brief]: A brief is the plugin's one document saying what the product is, who it is for and why.
[^skill]: A skill is a set of instructions Claude follows for one step, run as a slash command.
[^spec]: A spec is the plugin's document for what one capability of the product should do, and how we will know it does.
