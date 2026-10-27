---
name: brief
description: Write or change the product brief, the one short document at docs/brief.md that says what the product is, who it is for, why it exists and how we will know it works. Use whenever someone wants to start a new product, write or update a brief, a product vision or a one-pager, or capture what the product is and for whom before any specs are written, even if they don't say "brief". Not for one feature or capability; that is a spec.
---

# Brief

The brief says what the product is, who it is for, why it exists and how we will know it works.
A product has one, at `docs/brief.md`, edited in place; git is its history. Specs are written
against it, one per capability, so the brief holds only what is true of the whole product.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it saves rounds. A new brief starts from
[assets/template.md](assets/template.md). Read these with the Read tool, not the shell, so the
person is not asked to approve a command.

## What to read

The brief records what the person intends, which only they know. So draft from what they said in
this conversation and from what they point you to, such as a document, a link or notes. If
`docs/brief.md` exists, read it and change it rather than starting again; the documents it
already links to count as pointed to. Don't read anything else on your own, not the README, the
code or a connected service: what a repository holds today can quietly pass for what the product
is meant to be. If something would help, ask first ("There's a README here; shall I read it?")
and read it only if they say yes.

## Shape it with the person

Usually the person has already talked the product through. Draft from that, carrying over every
fact they gave that the brief's sections hold, such as who does what; where the
conversation changed its mind, the latest word wins. Only when there is nothing to draw on, ask
what they are building and for whom first.

Write only what they said or showed you, as rubric check 8 describes, and link each fact taken
from a document to it, as check 9 does. When they mention something that belongs to a later
stage (rubric checks 2 and 7), leave it out and tell them where it goes: how one capability
behaves goes in its spec, so suggest `/spec`; a technology or design they have decided goes in an
ADR (architecture decision record), and one they have not becomes an open question.

Then ask about what the draft or the review leaves open: say how many questions there are and
ask only the first, as one question rather than two joined together. The others wait in the
brief, so leave them out of that reply entirely: describe the draft by what it says, never by
what it lacks ("nothing yet on who else is involved" names a question), and report what you or
the review changed without naming the gaps that remain. Ask the next once the first is settled,
playing back what you have understood. Settle each answer before moving on: take the part they
answered and ask again about the rest, because silence is not agreement. If the person has said
not to ask now, or would rather not answer, give only the count: no question and no list of what
the questions cover. An open question goes only when their answer is written into the brief.

## Review

When the brief is written, start the `sdlc:brief-reviewer` agent in the foreground, not in the
background, and give it the brief's path; it reads everything else it needs itself. Wait for its
report before touching the brief again, so the report matches the brief.

Fix every finding you can and run the reviewer again, for up to ${user_config.review_rounds}
reviews in all, counting the first. If no number appears in that sentence, the plugin's Review
rounds setting has not been saved: write the brief as usual, then stop before the first review,
tell the person the brief is unreviewed, and ask them to run `/plugin configure sdlc@sdlc`, type
a number next to Review rounds, choose Save configuration, run `/reload-plugins` and then ask
you for the review. Never pick a number yourself. After any edit to the brief, run the next
review, so the report the person gets is about the brief as it now stands; after the last
review, edit no further. Fix by making the brief accurate, never by dropping or hedging what the
person said to get a pass. A finding under Needs a person goes to them as a question rather than
a fix you invent, and into Open questions while a review remains to check that edit. If the last
review still fails, stop and show the person the report. The count starts again when the person
replies.

Finish by giving the person the brief's path and the reviewer's final report, except the open
questions and decisions it lists for the person: give their count and ask the first, as above.
Leave committing to them.
