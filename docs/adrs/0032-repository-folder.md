---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: 2026-11-14
supersedes: 0022
---

# Find the repository from the file each hook acts on, through one shared piece of code

## Question

How does each of the plugin's hooks[^hook] find the git repository it works in?

## Decision

Chosen: every hook finds the repository by going up from the file it acts on to the nearest folder
holding git's `.git`, through one piece of code all hooks share. A relative path counts from the
folder Claude's shell is in. A hook with no file looks in the session folder[^session], then in the
repositories directly inside it. One rule then serves a plain session and a Claude project
thread[^thread] alike.

## Background

The hooks treat the session folder as the repository, but a project thread's holds its repositories
one level down. There, the build's[^build] hook recorded no commit
for its reviews, so it refused every correction check[^check]. [ADR 0022](0022-review-repository-folder.md) already solved this
for document reviews alone,; the other hooks never followed it.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Keep using the session folder | Rejected | Wrong in every project thread |
| Use the folder Claude's shell is in | Rejected | Claude may never have left the session folder |
| Look for a repository among the session folder's subfolders | Rejected | A project thread holds several, and nothing says which is meant |
| Have each skill tell the hook the repository | Rejected | Nothing would check the folder Claude typed, as [ADR 0022](0022-review-repository-folder.md) found |
| Go up from the file each hook acts on, through shared code | Chosen | The file's place on disk decides, in every kind of session |

## Consequences

- Good: every hook in scope works wherever the repository sits.
- Good: one piece of code holds the rule, so a correction reaches every hook.
- Good: Claude gets the lifecycle[^lifecycle] rules when any of the session's repositories uses them.
- Bad: every hook that acts on a file walks up the folders each time it runs.

## Out of scope

- A file outside any repository, for which the session folder stands in.
- Repositories nested more than one level below the session folder, for a hook with no file.
- Scripts Claude runs itself, which take the folder or file Claude names, as today.
- The hook that checks a command's git branch, which already uses the command's folder.
- The plugin's feedback draft, which has no file; its reviewing agent still searches the session folder.

## How we'll check

Applies to: any hook that judges or records anything about a repository or its files.

1. Inspection: no hook in scope works out the repository other than through the shared code.
2. Test: unit tests run each hook from a session folder above the repository.
3. Test: a sample build run from a folder above the repository passes its correction check.
4. Demonstration: an install in a project thread's layout gets the lifecycle rules and status checks.

## Open questions

### 1. Restate what the review hook keeps from [ADR 0022](0022-review-repository-folder.md)

The review hook's `Repository:` line and refusals would be stated only in a superseded ADR.

> **Proposed:** Restate them in Technical detail.
>
> **Why:** A superseded ADR is replaced whole.

## Technical detail

**The shared code.** One module in `scripts/` gives two functions:

- *The repository of a path.* A relative path is first made full against the hook event's `cwd`,
  the folder Claude's shell is in, then `CLAUDE_PROJECT_DIR`, then the hook's own working folder.
  The function goes up from the path's folder to the first folder holding `.git`, as a folder or a
  file, so worktrees and submodules count.
- *The repositories of the session.* The session folder, if it is a repository; otherwise each
  repository directly inside it.

**Each hook.**

- The hooks that check document statuses, references between documents and the size of recorded
  practices judge where a written file sits, such as "directly in `docs/plans/`", relative to that
  file's repository.
- The hook that relays document reviews keeps the behaviour
  [ADR 0022](0022-review-repository-folder.md) gave it, now through the shared code.
- The hook that relays the build's reviews takes the repository from the plan file named on the
  first line of each reviewer's request. It keeps that repository with the commit the reviews saw,
  and reads the current commit there before the correction check starts.
- The session-start hook gives Claude the plugin's `docs/lifecycle.md` when any of the session's
  repositories has a brief or a spec with a lifecycle status.

[^hook]: A hook is a script Claude Code runs automatically at set moments, such as before Claude writes a file or starts an agent.
[^session]: The session folder is the folder Claude Code was started in.
[^thread]: A Claude project thread is one conversation inside a project in the Claude app; its session folder holds each of the project's repositories in a folder of its own.
[^build]: The build is the plugin's step that writes the code for one plan, a document setting out one piece of work, and then has separate agents review it.
[^check]: A correction check is a separate agent's check that the corrections made after a review were made, and broke nothing.
[^lifecycle]: The lifecycle is the plugin's set of documents and the rules for moving each one from draft to settled.
