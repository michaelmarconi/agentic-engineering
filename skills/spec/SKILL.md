---
name: spec
description: Write or change a spec, the living document that says what one capability of a product should do and how we will know it does, as EARS rules with Given/When/Then scenarios. Use whenever someone wants to specify, describe or pin down a feature or behaviour before building it, change what an existing feature should do, answer a spec's open questions, or mark a spec ready to build, even if they don't say "spec".
---

# Spec

A spec describes one capability of the product (something a person or another system can do
with it) as the system should behave now. It says what the system does, never how it is built,
so the code can change without the spec going stale. One capability has one spec, edited in
place; git is its history.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it saves rounds. New specs start from
[assets/template.md](assets/template.md). Read these with the Read tool, not the shell, so the
person is not asked to approve a command.

## Find the spec

Specs live at `docs/specs/<capability>.spec.md`, named for the capability in lowercase with
hyphens, possibly in subfolders. Search `docs/specs/` before creating one: if a spec already
covers the capability, change it instead, because two specs for one capability will drift apart.
If `docs/brief.md` exists, read it so the spec fits the product.

## Shape it with the person

Usually the person has already talked the idea through in this conversation. Draft from that,
and from whatever they point you to, such as code, tickets or notes; research what else you
need, as that is part of writing a spec. Where the conversation changed its mind, the latest
word wins. Only when there is nothing to draw on, ask about the idea first.

Then ask about what the draft or the review leaves open: say how many questions there are, ask
only the first (a conflict with another spec, or a decision the review says needs the person,
comes first), and do not mention any of the others anywhere in that reply, not even in passing
or in a report of what you or the review changed (they are in the spec); ask the next once it is
settled, playing back what you have understood. If the person has said not to ask now, give the
count and leave the questions in Open questions. Settle each answer before moving on: if the
person answers part of what you asked, take that part and ask again about the rest, because
silence is not agreement; if they ask what you think, recommend something and wait for them to
accept it. If they would rather not answer now, leave the rest in Open questions.

Never fill a gap with a guess, including the person and situation in the Problem: if the
person has not told you who is stuck and how, write only what you were told, without adding a
purpose or detail of your own, say the rest is not known yet and ask in Open questions. Use
only people the person named, anywhere in the spec; scenario values such as
`user@example.com` need no name.
An unknown goes into Open questions, worded so it can be answered. When the person names how
something should be built (a library, a service, a named bucket or database, a design), keep
the behaviour it serves and leave the choice out of every section, even when they state it as
settled: the spec should still hold if the choice changes. If it is already decided, suggest
recording it as an ADR (architecture decision record); if not, make it an open question. When
an unknown can only be settled by trying something, suggest a spike: a throwaway experiment.

Add only behaviour the person asked for or agreed to. A case they have not covered, such as who
may not use the feature, what happens on an error, or what happens when a rule's condition does
not hold, is an open question, not a rule you choose: a rule for paid invoices says nothing
about unpaid ones. Write each requirement as rubric checks 5 to 8 describe: one EARS rule, scenarios that
add concrete cases, and a Verified by line.

An open question the person has seen is settled only by their answer: written into the spec,
or, for a technical choice, recorded in an ADR they accept, after which the question goes.
Never remove or reword such a question without that answer, and moving it to another section,
or noting that someone will decide later, leaves it open. A decision the review raises is
settled the same way: write the person's choice into the part of the spec it is about, even if
the choice is to keep the meaning, so the next review can see it is settled.

## Status

The `status:` frontmatter says how far the spec is: Draft, Ready to build or Built.

- Write new and changed specs as Draft. Changing a spec that is Ready to build or Built returns
  it to Draft, because what was agreed or built no longer matches: set the status to Draft
  first, as a plugin hook refuses any other change to such a spec.
- Set Ready to build only when the person asks for it, the spec has no open questions (rubric
  check 9), nothing is left under the review's Needs a person, and the review below has passed
  on the spec as it stands; make it its own, last edit, after that review. Ready means the person
  agreed to this text, so if you wrote or changed anything they have not seen since, show it and
  wait for their reply first; agreement given before they saw it does not count, even a request
  to fix small things and carry on. So never set Ready in the same reply as a change to the
  spec's content. If questions
  remain, say how many, ask the first and leave the spec as Draft, even if the person says they do not matter:
  offer to settle them now instead.
- Never set Built. Only the build step does, once its review finds every requirement verified.

## Review

When the spec is written, start the `sdlc:spec-reviewer` agent in the foreground, not in the
background, and give it the spec's path; it reads everything else it needs itself. Wait for its
report before touching the spec again, so
the report matches the spec. It reports pass or fail for each rubric check with evidence, other
findings, decisions that need the person, and suggestions.

Fix every finding you can and run the reviewer again, for up to ${user_config.review_rounds}
reviews in all, counting the first. If no number appears in that sentence, the plugin's Review
rounds setting has not been saved: write the spec as usual, then stop before the first review,
tell the person the spec is unreviewed, and ask them to run `/plugin configure sdlc@sdlc`, type a
number next to Review rounds, choose Save configuration, run `/reload-plugins` and then ask you
for the review. Never pick a number yourself. After any edit to the spec's content, even
adding an open question the review raised, run the next review, even if a failure that needs the person remains, so the report
the person gets is about the spec as it now stands; after the last review, edit no further. A
decision under Needs a person goes to them as a question rather than a fix you invent. If the
last review still fails, stop and show the person the report. The count starts again when the
person replies.

Suggestions are optional behaviour the spec works without; pass them on to the person as
options to add, and do not hold the spec back for them.

Finish by giving the person the spec's path and the reviewer's final report, except the open
questions and the decisions it lists for the person, including ones you added: give their count
and ask the first, as above. Leave committing to them.
