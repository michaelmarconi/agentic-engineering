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

Chosen: every hook that acts on a file finds the repository by going up from that file to the
nearest folder holding git's `.git`, through one piece of code all hooks share. A relative path
is read from the folder Claude's shell is in, or else from the session folder[^session]. A hook with no
file looks in the session folder and the repositories directly inside it. One rule then serves a session started in a repository and a Claude project
thread[^thread] alike.

## Background

The hooks treat the session folder as the repository, but a project thread's session folder holds
its repositories one level down. There, the build's[^build] hook could not record which commit
its reviews saw. So it could never tell a correction was committed, and refused every correction
check[^check]. [ADR 0022](0022-review-repository-folder.md) solved this for
document reviews alone.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Keep using the session folder | Rejected | Wrong in every project thread, and in any session started above the repository |
| Use the folder Claude's shell is in as the repository | Rejected | Often still the session folder; used only to complete a relative path |
| Look among the session folder's subfolders, for every hook | Rejected | With several repositories, a hook with a file could pick the wrong one |
| Have each skill[^skill] tell the hook the repository | Rejected | Nothing would check the folder Claude named, as [ADR 0022](0022-review-repository-folder.md) found |
| Go up from the file each hook acts on, through shared code | Chosen | The file's place on disk decides, in every kind of session |

## Consequences

- Good: every hook that acts on a file works wherever its repository sits.
- Good: one piece of code holds the rule for every hook.
- Good: Claude gets the lifecycle[^lifecycle] rules when any of the session's repositories uses them.
- Bad: every hook that acts on a file walks up the folders each time it runs.

## Out of scope

- A project without git: its files use the session folder, as today.
- Repositories nested more than one level below the session folder, for a hook with no file.
- Scripts Claude runs itself, which take the folder Claude names.
- The hook that checks a command's git branch, which already uses the command's folder.
- An issue drafted about the plugin, which has no file; the agent reviewing it still searches the session folder.

## How we'll check

Applies to: any hook that acts on a repository's files, or looks for the session's repositories.

1. Inspection: no hook in scope works out the repository other than through the shared code.
2. Test: unit tests run each hook from a session folder above the repository.
3. Test: a sample build run from a folder above the repository passes its correction check.
4. Demonstration: an install in a project thread's layout gets the lifecycle rules and the checks on status changes.

## Open questions

- None.

## Technical detail

**The shared code.** One module in `scripts/` gives two functions:

- *The repository of a path.* A relative path is first made full against the hook event's `cwd`,
  the folder Claude's shell is in, then the session folder: `CLAUDE_PROJECT_DIR`, or the hook's own
  working folder when that is unset.
  The function goes up from the path's folder to the first folder holding `.git`, as a folder or a
  file, so worktrees and submodules count.
- *The folders of the session.* The session folder, then each repository directly inside it.

**Each hook.**

- The hooks that check the status field of the plugin's documents, references between documents,
  and the size of the project's recorded working rules for agents judge where a written file sits,
  such as directly in the plans folder, relative to that file's repository.
- The hook that starts the review agents for a document works as before, now through the shared code. Each skill
  gives the reviewed document's full path on the first line of each review request; a line may
  name several files. Just before the agent starts, the hook finds the repository holding them,
  rewrites that line to name each file relative to it, and adds a second line,
  `Repository: <the repository's full path>`. A relative path is read from that folder first. The hook
  refuses to start the agent, and says why, if no named file exists, or if the files sit in
  different repositories. Each agent reads and searches only inside the `Repository:` folder, and
  if it still cannot read the document, it reports an error instead of a result.
- The hook that starts the build's review agents, and records which commit they saw, takes the repository from the plan file named on the
  first line of each reviewer's request. It keeps that repository with the commit the reviews saw,
  and reads the current commit there before the correction check starts.
- The session-start hook gives Claude the lifecycle rules when any of the session's folders has a
  product brief, or a specification document with a lifecycle status.

[^hook]: A hook is a script Claude Code runs automatically at set moments, such as before Claude writes a file or starts an agent.
[^session]: The session folder is the folder Claude Code was started in.
[^thread]: A Claude project thread is one conversation inside a project in the Claude app; its session folder holds each of the project's repositories in a folder of its own.
[^skill]: A skill is one of the plugin's sets of instructions Claude follows for one step.
[^build]: The build is the plugin's step that writes the code for one plan, a document setting out one piece of work, and then has separate agents review it.
[^check]: A correction check is a separate agent's check that the corrections made after a review were made, and broke nothing.
[^lifecycle]: The lifecycle is the plugin's set of documents and the rules for moving each one from draft to settled.
