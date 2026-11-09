---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
date: 2026-11-09
---

# Mark up documents in a GitHub pull request review

## Question

Where does a person mark up one of the plugin's documents, so they can comment on it freely and
then hand every comment to Claude at once?

## Decision

Chosen: in a draft GitHub pull request, using GitHub's own review, where comments wait unseen
until the person submits them together. GitHub already holds the comments back, threads each reply
under its comment and keeps the record beside the file.

## Background

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. Its
skills write a project's documents, such as specs[^spec] and ADRs[^adr], as files in the project's
repository. A person reviewing one today tells Claude what to change, one point at a time, but
wants to mark up the whole document as they would a contract and hand over every comment in one go.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| A GitHub pull request review | Chosen | Batches comments and threads replies already; seconds per round when tried |
| A copy of the file in Claude Docs, claude.ai's shared documents | Rejected | Each comment starts Claude working, so a round took minutes; claude.ai only |
| The document posted into the chat | Rejected | Adds the whole document to the conversation every round |
| A review tool running beside Claude | Rejected | A cloud session cannot reach it, and every colleague must install it |
| Comment marks written into the file | Rejected | No threads or resolving, and the marks sit in the document itself |
| Every common code host, not just GitHub | Rejected | No one needs another host yet |

## Consequences

- Good: comments, replies and what was resolved stay on the pull request, beside the file.
- Good: the same review works from a desktop session and from a cloud session; only the hand-back differs.
- Bad: the person moves between Claude and GitHub in every round.
- Bad: comments go on the file's source text, not on the rendered page.
- Bad: closing the pull request does not remove comments, and anyone can read them in a public repository.
- Bad: the skill breaks the plugin's rule that skills assume no particular code host.

## Out of scope

- Code hosts other than GitHub, including GitHub's self-hosted edition.
- When the plugin's reviewer agents check a marked-up document; [ADR 0026](0026-markup-review-timing.md) decides that.
- How the skill is tested; [ADR 0027](0027-github-skill-tests.md) decides that.
- Deleting the review branch from a cloud session, which the session's network refuses.

## How we'll check

Applies to: how the markup skill takes a person's comments and answers them.

1. Test: given one submitted review, Claude replies to each comment, resolves what it handled and merges nothing.
2. Test: the skill stops, and says how to set up access, when it cannot reach the repository on GitHub.
3. Demonstration: a trial with the installed plugin marks up an already committed document, from start to merge.

## Open questions

- None.

## Technical detail

**Access.** Before anything else, the skill checks that the repository's remote is on
github.com and that Claude can reach GitHub, through `gh` signed in or the session's GitHub
tools. If neither works, it stops and says how to set one up. Running the skill is the person's
request to push, open a pull request and reply on it, as `AGENTS.md` rule 10 requires; rule 11
names this skill as its one exception to assuming no host.

**Start.** Claude pushes the person's branch if it has never been pushed, creates
`markup/<document file name>` from it, and opens a draft pull request from that branch back into
the person's branch. An open markup pull request for the same document is picked up instead,
including when the skill is run again in a new session. A pull request shows only the files it
changes. If the document has uncommitted edits or was never committed, Claude's first commit
holds them. Otherwise that commit adds `<!-- Marked up in a pull request -->` as the document's
last line. Claude then tells the person to press the file header's "expand all lines" button and
comment on any line.

**A round.** The person comments with "Start a review" and sends the comments with "Submit
review". In a desktop session they then tell Claude "markup done". In a project thread, GitHub
sends the submitted review to the thread, which starts Claude. Claude never polls. Before acting,
Claude checks the branch is where it left it. A commit the person made, such as an accepted
suggestion, is kept; anyone else's is shown, and Claude asks before going on. It then:

1. reads every comment of every review submitted since the last round, plus any single
   comments, acting only on the person who started the markup;
2. makes every change in one commit, removing the line `<!-- Marked up in a pull request -->` in
   the first round that edits;
3. replies in each thread: an answer for a question, the exact wording for a GitHub suggestion,
   or what it needs for a comment it cannot act on, leaving that thread open;
4. resolves each thread it handled, and ends with one summary pointing to GitHub's "Changes since
   your last review".

**End.** The person merges. Claude merges or approves only when the person explicitly asks. If no
round edited the document, Claude closes the pull request instead. If the person merges anyway,
the marker line lands; the next markup of that document removes it. After the merge, Claude
reminds the person to pull the merged branch before running the document's own skill.

**Evidence.** On 9 November 2026, a draft pull request in a private test repository changed only a
spec's last line. GitHub's API refused a comment on an unchanged line far from that change. In the
browser, after expanding the hidden lines, the same comment was accepted and stored against its
line. Claude replied to it and resolved it through the API. GitHub marked the thread "Outdated" at
once, but still showed it beside its line after a reload. The same day, a cloud project thread
subscribed to that pull request received each new review comment as an event. In an earlier trial,
handling one submitted review took 13 to 25 seconds, against about two and a half minutes for the
Claude Docs copy.

[^spec]: A spec says what one capability of a product should do.
[^adr]: An ADR, architecture decision record, records one technical decision and why it was made.
