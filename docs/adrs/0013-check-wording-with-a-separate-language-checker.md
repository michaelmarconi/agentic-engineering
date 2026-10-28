---
# Change status only through the sdlc plugin's skills. A hand edit skips the lifecycle checks.
status: Draft
date: 2026-10-28
---

# Check wording with a separate language checker

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. The
plugin helps a person write a software project's documents, such as specifications and records
of technical decisions. While Claude writes a document with the person, we call it the drafting
agent. ADR 0010 has every document reviewed once by a reviewer agent: a separate instance of
Claude, started with its own instructions and none of the conversation, which checks the
document against a list of pass-or-fail checks for that kind of document.

The drafting agent has been in the conversation, so the team's shorthand reads as plain to it.
Its documents fill up with words a newcomer cannot follow: names used only inside the team,
unexplained abbreviations, figures of speech, and terms from the product's field with no
definition. Only one kind of document, the product brief, had a check on wording, and the
others had none. The documents are meant to be read by anyone joining the project, so the
wording needs a check on every document, judged by someone who has not seen the conversation.

The lifecycle page now states the rule to check against: computing terms may be used freely; a
term from the product's field gets a footnote defining it where it first appears; anything else
a newcomer would not know is rewritten in plain words.

## Considered Options

- **Add the wording rule to every kind of document's list of checks, for its own reviewer to
  apply.** Rejected: it caught fewer problems. We planted 60 wording problems in 12 documents
  about two made-up products and ran each review 5 times. With the rule added to the list of
  checks, the reviewers found 88% of them. A separate checker given the same rule found 96%.
  The gap was widest for terms from the product's field that read like ordinary English, such
  as "dispensing fee": 72% against 90%.
- **A separate language checker, run beside each reviewer.** One shared agent, given only the
  document and the rule, reads every phrase as a newcomer would. It runs at the same time as the
  document's own reviewer, so the review takes no longer. The drafting agent corrects what both
  report, once, and the correction checker checks both sets of corrections.
- **No automated check: tell the drafting agent to write plainly.** Rejected: the drafting agent
  is the one who cannot see its own shorthand, which is why every document is reviewed by
  someone else.

## Decision Outcome

Chosen option: a separate language checker, run beside each reviewer, because it found more of
the planted problems than the same rule in each list of checks, and found as many of the other
kinds of problem.

### Consequences

- Good: every kind of document, including those written later, gets the same wording check from
  one agent, so the rule is kept in one place.
- Good: in the same test, the reviewers found every other planted problem whether or not the
  language checker ran beside them, and documents with no planted problem drew no more false
  alarms.
- Bad: each review costs about 17% more, since one more agent runs.
- Bad: the checker raises more complaints that turn out to be wrong: about 0.8 per document in
  the test, against 0.1 for the reviewers, such as flagging the product's own name. The drafting
  agent then rewrites a phrase that was already fine.
- Bad: the hook that hands the correction checker the review now has to collect two reports per
  document, which may finish in either order.

### Confirmation

Applies to: any step in which a skill reviews a document it wrote.
Checked by: automated tests. Unit tests feed the hook that collects the reports both orders in
which the two reports can arrive, and check that the correction checker is refused unless both
are on record. Tests that run each skill on sample conversations check that the language checker
ran exactly once beside the reviewer and that the correction checker was given its report.
