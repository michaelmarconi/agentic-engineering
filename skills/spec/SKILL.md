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
reviewer will apply, so writing to it leaves less to correct. New specs start from
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
something should be built (a library, a service, a named bucket or database, a design), keep the
behaviour it serves and leave the choice out of every section, even when they state it as
settled: the spec should still hold if the choice changes, and tell the person you left it out.
If it is already decided, suggest recording it as an ADR (architecture decision record); if not,
make it an open question. When an unknown can only be settled by trying something, suggest a
spike: a throwaway experiment. When the person wants the spec to refer to the brief, another
spec, an ADR or a plan, by hyperlink, path or title, leave it out (rubric check 11) and tell them
why: that document can change or be deleted without this spec being touched, so the reference
would go stale.

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

The `status:` frontmatter says how far the spec is: `📝 Draft`, `🟢 Ready to build` or `✅ Built`,
written exactly so, emoji first. A status written as a bare word, from before the emoji, gets its
emoji in your next edit.

- Write new and changed specs as `📝 Draft`. Changing a spec that is `🟢 Ready to build` or
  `✅ Built` returns it to `📝 Draft`, because what was agreed or built no longer matches: set the
  status to `📝 Draft` first, as a plugin hook refuses any other change to such a spec.
- Set `🟢 Ready to build` only when the person asks for it, the spec has no open questions (rubric
  check 9), nothing is left under the review's Needs a person, and the review below has ended
  with a pass on the spec as it stands, from the review itself or from the correction check
  after it; make it its own, last edit, after that review. `🟢 Ready to build` means the
  person agreed to this text, so if you wrote or changed anything they have not seen since, show it and
  wait for their reply first; agreement given before they saw it does not count, even a request
  to fix small things and carry on. So never set `🟢 Ready to build` in the same reply as a change to the
  spec's content. If questions
  remain, say how many, ask the first and leave the spec as `📝 Draft`, even if the person says they do not matter:
  offer to settle them now instead.
- Never set `✅ Built`. Only the build step does, once its review finds every requirement verified.

## Review

Every spec is reviewed once, corrected once, and then the corrections are checked. The
sequence is fixed so it always ends with a clear result: further rounds of review find little
more, and each round of corrections brings new mistakes.

1. **Review.** When the spec is written, start the `sdlc:spec-reviewer` agent in the foreground,
   not in the background, with this request, its first line exactly as shown, since a plugin
   hook reads that line to keep a copy of the spec as reviewed:

   ```
   Document: <the spec's path>
   Review this spec.
   ```

   It reads everything else it needs itself. Wait for its report before touching the spec. If
   it passes with nothing under Needs a person, go straight to handing over.
2. **Correct, once.** Read the rubric again, then correct only what the report lists: each
   failed check and each item under Other findings. A decision under Needs a person
   becomes an entry in the spec's Open questions, never a guess at the answer. Leave
   suggestions alone and change nothing else, since an edit beyond the report is the likeliest
   way to break something. Wait until every edit has succeeded. If nothing in the report was
   yours to correct, there is nothing to check: go straight to handing over.
3. **Check the corrections.** Start the `sdlc:correction-checker` agent in the foreground with
   this request, and add nothing to it: the hook attaches the report and the spec as reviewed,
   word for word.

   ```
   Document: <the spec's path>
   Check the corrections.
   ```

   If the hook refuses to start it, do what its reason says. If the check fails, stop: change
   the spec no further, and show the person the check's report. Do not review or correct
   again; what happens next is their call.

After the sequence, edit the spec only when the person asks. When they change it or ask you to,
run the sequence again on the changed spec.

Whether the check passed or failed, end with the hand-over. It is what the person acts on, so make
it hard to miss anything. Give them the spec's path, the review report and the check's report, if
there was one, leaving out the decisions they list for the person. Then say how many items must be
settled before the spec can move on: its open questions, plus any correction the check found not
made or broken. Say you will take them one at a time, rather than asking whether to, and ask the
first only, as a single question, giving any examples as possible answers rather than further
questions; if the person has said not to ask now, ask nothing. Name the count only, not the items:
each comes up when you reach it. List the reviewers' suggestions separately, as optional: they never
hold the spec back. Leave committing to them.
