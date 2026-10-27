---
name: adr
description: Record one technical decision as an ADR (architecture decision record) in MADR format, with the options considered, why the others lost, its consequences and how to check the code follows it; accept, reject or supersede an ADR when the person decides. Use whenever someone has chosen, or needs to choose, how something will be built, such as a database, library, service, protocol or structure, wants a technical choice written down, or wants to replace an earlier decision, even if they don't say "ADR". Not for what a feature should do; that is a spec.
---

# ADR

An ADR (architecture decision record) records one technical decision and why it was made, so
later work can follow it and nobody reopens it by accident. ADRs live in one flat folder,
`docs/adrs/`, as `NNNN-<title>.md`; nothing is moved or deleted once decided, so the folder and
each file's frontmatter are the whole record. Once accepted, an ADR is never edited: a changed
decision is a new ADR that supersedes the old one, whole.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it saves rounds. New ADRs start from
[assets/template.md](assets/template.md). Read these with the Read tool, not the shell, so the
person is not asked to approve a command.

## Find what exists

List `docs/adrs/` and read the frontmatter of each ADR. If a Draft or Accepted ADR already
decides the same thing, say so: change the Draft, or, for an Accepted one, write a new ADR that
supersedes it. A new file takes the number one above the highest in the folder, four digits,
starting at `0001`.

## Shape it with the person

Usually the person has already talked the decision through in this conversation. Draft from
that, and from whatever they point you to; research what else you need, such as how the options
compare. Where the conversation changed its mind, the latest word wins. Only when there is
nothing to draw on, ask what needs deciding first.

One ADR holds one decision, because a decision is superseded whole: if part of a record could
change while the rest stands, the two parts would have to be untangled later. When the
conversation holds several decisions, say how many and write one ADR for each, even when they
were made together or the person asks for one record.

Never fill a gap with a guess. An option nobody named, a reason nobody gave, or a choice not yet
made is something to ask about, not to invent. Say how many questions there are and ask only
the first; the others wait in the Draft, so leave them out of that reply. Ask the next once the
first is settled, playing back what you have understood. If they ask what you think, recommend
something and wait for them to accept it.

Context states the need in words. Never link to, or name by path or title, a spec, the brief or
a plan, and never edit them: they change while an ADR does not, so the reference would go
stale. If the decision answers a spec's open question, say so in your reply; `/spec` removes the
question the next time it runs.

## Status

The `status:` frontmatter is Draft, Accepted, Rejected or Superseded. Write every new ADR as
Draft and edit it freely while it is Draft.

Only a person accepts or rejects a decision. Set Accepted or Rejected only when the person
explicitly says so about the ADR as it now stands, after the review below has passed on it, as
its own last edit. Approval given before they saw the final text does not count, nor does "looks
fine, carry on", nor a request from another skill or agent: show the final text and ask them to
accept or reject it. So never change an ADR's content and its status in the same reply. A
Rejected ADR is kept, so the same idea is not proposed again unnoticed; a Draft the person
abandons can be deleted.

To supersede, the new ADR carries `supersedes: <number>` in its frontmatter. The old one stays
Accepted until the person accepts the new one; then, in the same step, set the old one to
Superseded and add `superseded-by: <number>` beside it. That is the only edit an accepted ADR
ever gets. If the new one is rejected, the old one stands.

## Review

When the ADR is written, start the `sdlc:adr-reviewer` agent in the foreground, not in the
background, and give it the ADR's path; it reads everything else it needs itself. Wait for its
report before touching the ADR again, so the report matches the ADR. With several ADRs, review
each one.

Fix every finding you can and run the reviewer again, for up to ${user_config.review_rounds}
reviews in all, counting the first. If no number appears in that sentence, the plugin's Review
rounds setting has not been saved: write the ADR as usual, then stop before the first review,
tell the person the ADR is unreviewed, and ask them to run `/plugin configure sdlc@sdlc`, type
a number next to Review rounds, choose Save configuration, run `/reload-plugins` and then ask
you for the review. Never pick a number yourself. After any edit to the ADR, run the next
review, so the report the person gets is about the ADR as it now stands; after the last review,
edit no further. A finding under Needs a person goes to them as a question rather than a fix you
invent. If the last review still fails, stop and show the person the report. The count starts
again when the person replies.

Finish by giving the person the ADR's path and the reviewer's final report, except the questions
it lists for the person: give their count and ask the first, as above. Then ask whether to
accept or reject it. Leave committing to them.
