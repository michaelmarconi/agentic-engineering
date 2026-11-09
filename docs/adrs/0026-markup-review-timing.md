---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
date: 2026-11-09
---

# Review a marked-up document when its own skill next runs, not while it is marked up

## Question

When do the plugin's reviewer agents check the changes Claude makes while a person comments on a
document in a pull request?

## Decision

Chosen: not during the markup. The document's own skill[^skill] reviews the text as it stands when
it next runs on that document, and always before it changes the document's status[^status].

## Background

[ADR 0025](0025-document-markup-place.md) lets a person comment on a document in a GitHub pull
request, and Claude changes the document once per round of comments. Elsewhere, every change a
skill makes to a document is checked before the person sees it, by the review sequence
[ADR 0010](0010-correction-check.md) decides. A markup skill needs its own answer to when that
check runs, because the person repeats its rounds many times.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Review after every round | Rejected | Adds minutes to every round of a loop the person repeats |
| Review once when the markup ends, posting findings as comments | Rejected | The last round changes the text, so the status change reviews it again |
| Review when the document's own skill next runs | Chosen | One review, of the final text, by the skill that owns the document |

## Consequences

- Good: a round takes seconds, so the person can go round as often as they like.
- Good: the skills stay apart: the markup skill never changes a status, and no other skill handles markup.
- Bad: a marked-up draft sits unreviewed until its own skill next runs.
- Bad: the markup skill is the one skill whose changes reach the person before a review.

## Out of scope

- Which documents the markup skill accepts, and what it tells the person at the end; the skill's own page sets those.

## How we'll check

Applies to: what the markup skill does after it changes a document.

1. Test: a round starts no reviewer agent and leaves the document's status and frontmatter unchanged.
2. Inspection: the plugin's rules for skills, its lifecycle page and its README name the markup skill as the exception.

## Open questions

- [ADR 0010](0010-correction-check.md) says that when the person later asks for changes, "the same sequence runs again on the changed document". This ADR makes an exception for markup. Proposed: keep ADR 0010 as it stands and record the exception here, with the lifecycle page and README saying so, rather than supersede ADR 0010 with a copy that adds one exception. Which do you want?

## Technical detail

The markup skill never edits a document's frontmatter, so it never changes a status. Every skill
that owns a document already reviews it when run to change it, and the lifecycle's rule that "a
status that needs a passing review ... is set only after a review of the text as it stands has
passed" covers the status change itself. So no other skill changes.

Three texts gain one sentence each, naming the exception: rule 4 in `AGENTS.md`, the Review
process section of `docs/lifecycle.md`, and the README's promise that every document is reviewed
before the person sees it.

[^skill]: A skill is one step of the plugin, such as `/sdlc:spec`, which writes and accepts specs.
[^status]: A status is a field at the top of a document, such as `📝 Draft` or `👍 Accepted`, saying how far along it is.
