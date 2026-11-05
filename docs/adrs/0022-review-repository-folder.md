---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-11-05
---

# Find each review's repository from the document's full path

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. Its
skills, sets of instructions Claude follows for one kind of task, write a project's documents
and have each one reviewed by agents: separate instances of Claude, each started with its own
instructions and a short request, and none of the conversation. Three kinds of agent take part:
a reviewer, which checks the document against a list of checks; an agent that checks the
document's wording; and an agent that checks, after the review, that the corrections it asked
for were made. Each is told which document to judge by a first line such as
`Document: <path>`, where the path is relative to the project's top folder. A hook, a script
Claude Code runs just before and after each agent, reads that line to keep a copy of the
document as reviewed for the agent that checks the corrections, as architecture decision record
(ADR) 0011 decided.

Every one of them, the hook included, reads that path from the folder Claude Code was started
in. Usually that is the project's top folder, and the paths are found correctly. But a person
may start Claude Code in a folder above the project, such as one holding several projects, or
work in a session that holds several repositories. Then the document is not found where they
look, and neither are the other documents a reviewer compares it with, such as the other
documents saying what each capability should do, which it reads to check that no two of them
state the same thing. A check with nothing to compare against passes, so a review can report a
pass on a document it never fully checked, and the hook can keep no copy of the document.

The plugin's audit step, which looks for places where the code and its documents disagree,
already handles this: its script prints the project's full path, and every agent's request gets
a second line, `Repository: <that path>`. The other skills have no script in their review step,
so they need another way to know the project's folder.

## Considered Options

- **Each agent searches for the document itself.** Rejected: an agent that searches for a
  document's relative path from a folder above several projects may find a file of that name in
  the wrong one, and nothing would tell it so.
- **The hook uses the folder Claude Code was started in.** Rejected: that is the folder that is
  wrong in exactly the case this decision is for.
- **Each skill adds a `Repository:` line with the project's full folder to the request.**
  Rejected: Claude would type the folder into each request with nothing checking it, and a
  mistyped or wrong folder would again leave a review checking nothing.
- **The hook remembers the full path of every file Claude writes, and matches the `Document:`
  path against them.** Rejected: a document may be reviewed in a session that did not write it,
  such as when reviewing an existing ADR, so the hook would have nothing to match.
- **Each skill gives the document's full path, and the hook works out the project from it.**
  Claude must use the full path anyway to write the document, so it gives the path it already
  wrote to. A line naming several files, as ADR 0018 allows, gives each file's full path. Just
  before the agent starts, the hook finds the top folder of the git repository holding the
  files. It rewrites the request's first line to name each file by its path relative to that
  folder, as today, and adds a second line, `Repository: <the folder's full path>`. If a file is
  not in a git repository, the folder Claude Code was started in stands in for it. The hook
  refuses to start the agent, and says why, if it finds no such file, or if the files sit in
  different repositories. Each agent reads and searches only inside the `Repository:` folder,
  and if it still cannot read the document, it reports an error instead of a result.

## Decision Outcome

Chosen option: each skill gives the document's full path, and the hook works out the project
from it, because the folder then comes from the files on disk, not from Claude's typing, and it
works whether or not this session wrote the document.

### Consequences

- Good: every review, wording check and correction check reads the document, and every other
  document it compares against, from the right project, whichever folder Claude Code was started
  in.
- Good: no review runs on a document that cannot be read: the hook refuses to start it, and an
  agent that still cannot read its document reports an error rather than a pass.
- Good: everything after the hook, the copy it keeps, the reports and the request to the agent
  that checks the corrections, still names the document by its path relative to the project, as
  before.
- Bad: the hook does more before every review agent starts: it must find the files and their git
  repository, and rewrite the request. It is one more thing that can go wrong in the step every
  review depends on.
- Bad: for a document outside any git repository, the hook still uses the folder Claude Code was
  started in, which may be the wrong one.
- Bad: a bug report or suggestion for the plugin itself is drafted in the conversation and never
  saved as a file, so it has no path to work from. Its reviewer, which checks that the draft
  repeats no names or details from the person's own project before it is made public, still
  searches the folder Claude Code was started in.

### Confirmation

Applies to: any request that starts a review agent, and any review agent that reads files.
Checked by: automated tests. Unit tests feed the hook requests that name a document by its full
path from a folder above the project, and check the rewritten request and the copy kept; and
requests naming a file that does not exist, or files in two repositories, and check the hook
refuses them. A test that runs a skill from a folder above the project checks that the review
found a mistake planted in the document. A test that starts a reviewer for a document that does
not exist checks that it reports an error.

## Open questions

- None.
