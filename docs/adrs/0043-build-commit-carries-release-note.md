---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: Accepted 👍
date: 2026-11-17
---

# Each build commit carries its release note, for the release skill to gather

## Question

Where does a build's[^build] draft release note live until the release, so the release
skill[^release] can draft good release notes?

## Decision

Chosen: the commit that ends each build carries one or more lines starting
`Release-note:` in its message, drafted from the plan[^plan] and its specs[^spec] while they are still available,
and the release skill gathers those lines from every commit since the last release. This is
chosen because git keeps the note with the code it describes, so it survives whatever
happens to the plan, needs no new file, and never causes a merge conflict between branches.

## Background

Good release notes say what users can now do. The plan and its specs say exactly that, but a
built plan may be deleted, or never given the status `✅ Built`, before the release. Notes guessed from commit
messages are much poorer. So the note must be written at build time and kept until the release.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| A `Release-note:` line in the build's last commit message | Chosen | Stays in the code's own commit, needs no new file, and no two branches edit the same text |
| Keep every plan, and draft the notes from plans at release time | Rejected | Built plans are meant to be thrown away, and a plan may be missing or never given the status `✅ Built` |
| A release-note section in each plan | Rejected | The plan must still be found at release time, so it has the same gaps |
| One small note file per change, gathered at release | Rejected | Adds a new file format to every project's repository |
| Draft entries in the changelog's Unreleased section | Rejected | Parallel branches edit the same lines and conflict, and not every project keeps a changelog |
| Draft the notes from commit history alone | Rejected | Commit messages describe code, not what users gain |

## Consequences

- Good: notes come from the plan and specs, the best account of each change.
- Good: no file is added to the project, and no changelog is needed.
- Bad: the plugin now writes its own data into commit messages, which it avoided before.
- Bad: a merge that throws away commit messages, such as a squash merge keeping only the pull
  request's title, loses the note.

## Out of scope

- How the release skill reviews and writes the notes.
- Work done without a build: the release skill drafts its notes from history.

## How we'll check

Applies to: the commit that ends a build, and how the release skill finds release notes.

1. Test: the message of the commit that ends each build holds at least one `Release-note:` line.
2. Test: given commits since the last release, the release skill's script returns every
   `Release-note:` line, including one inside a squash merge's message body.
3. Test: a commit with no such line is listed as having no note, for drafting from history.
4. Inspection: the build skill drafts each note from the plan and its specs, for users.

## Open questions

- None.

## Technical detail

**The line.** Each note is one line of the form `Release-note: <one sentence for the product's
users>`, written at the end of the message as a git trailer, which `git interpret-trailers` reads.
A build that delivers several things users would notice writes one line per thing. The line is
written whether or not the plan ends with the status `✅ Built`, since an unfinished build may still be merged.

**Gathering.** The release skill's script lists the commits reachable from the commit being
released and not from the last release. It reads every line that starts with `Release-note:`,
anywhere in each message, not only trailers at the very end, since a squash merge folds a
branch's messages into one body. It reports, for each note, its commit, and lists apart each
commit that changed files and carries no note.

**Merges.** A merge commit keeps the branch's commits, so their notes are found. GitHub's default
squash message lists the branch's commit messages in its body, so the notes are found there too.

[^release]: The release skill is the plugin's step that makes one numbered version of the product, with release notes, and publishes it where the project does.
[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed.
[^plan]: A plan is the plugin's document for one piece of work that builds part of a spec; its statuses include `✅ Built`, set when the build passes its reviews.
[^spec]: A spec is the plugin's document for what one capability of the product should do, and how we will know it does.
