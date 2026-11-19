---
name: spec
description: Write or change a spec, the living document that says what one capability of a product should do and how we will know it does: a one-sentence story, then numbered EARS rules, each with Given/When/Then examples and how we'll check it. Use whenever someone wants to specify, describe or pin down a feature or behaviour before building it, change what an existing feature should do, answer a spec's open questions, or accept a spec, signing off its text, even if they don't say "spec". Not for recording a technical choice (an ADR) or working out how to build it (a plan).
---

# Spec

A spec describes one capability of the product (something a person or another system can do
with it) as the system should behave now. It says what the system does, never how it is built,
so the code can change without the spec going stale. One capability has one spec, edited in
place; git is its history.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it leaves less to correct. Write in plain words, as the Plain
words section of [the lifecycle page](../../docs/lifecycle.md#plain-words) says: a language
checker holds every document to it. New specs start from
[assets/template.md](assets/template.md). Read these with the Read tool, not the shell, so the
person is not asked to approve a command.

The template's frontmatter holds `type: Spec`, which says what the document is. A spec written
before it has no `type:`, so add it with your next edit. The title never names the document's type,
as "Spec:" or "ADR:" in front of it would: the frontmatter's `type:` already says what it is.

## Find the spec

Specs live at `docs/specs/<capability>.spec.md`, possibly in subfolders, named for the capability in
two to five lowercase words joined by hyphens, each a word of the spec's title; a plugin hook
refuses a name that breaks this, and an edit that drops one of those words from the title. When the
existing specs sit in subfolders, put a new spec in the one it fits, and ask the person only when
none clearly does; never move existing specs to a layout of your own.

Never rename a document once its review has started: the review hook keeps the review under the
document's path, so a renamed document's corrections can't be checked. If the name no longer fits,
say so to the person, who can rename it once the review has ended.

Search `docs/specs/` before creating one: if a spec already covers the capability, change it
instead, because two specs for one capability will drift apart. If `docs/brief.md` exists, read it
so the spec fits the product. A spec says far more than the brief, and detail the brief doesn't
mention is never a reason to raise it. Only an outright contradiction with the brief's Goals, Out of
scope or Constraints is, such as a rule for something the brief puts out of scope (rubric check 15).
Write it into Open questions, proposing one of its two answers: change the spec to fit, or the
person changes the brief with `/brief`. Never edit the brief, or offer to: it changes only when the
person changes the product's intent. If they choose to change the brief, the question goes once the
brief no longer contradicts the spec.

## Shape it with the person

Usually the person has already talked the idea through in this conversation. Draft from that,
and from whatever they point you to, such as code, tickets or notes; research what else you
need, as that is part of writing a spec. Where the conversation changed its mind, the latest
word wins. Given a finished spike record from `docs/spikes/`, draft from its Finding and Next
steps, stating its evidence in the spec's own words, such as "all 20 sample files opened": a spike
record may be deleted at any time, so the spec never names it. Only when there is nothing to draw
on, ask about the idea first.

Settle what the spec is for before its requirements. Write the Story, one sentence saying when
the capability is needed, who wants it, what they want to do and the outcome they want, as rubric
check 2 says, and the In scope and Out of scope lists. Play these back to the person in a short
reply and ask whether they have it right, before you draft any requirement, unless they have
already agreed them in this conversation. If they asked you to write the spec now, or not to stop
and ask, draft it all and play the story and scope back at the hand-over instead, so they can
correct them there. If the story holds two outcomes someone could ask for
separately, such as importing and exporting, it is two capabilities: offer to split it into two
specs, and write one at a time. The first requirement then states the outcome the story asks
for (rubric check 12), and the others say how it holds in particular cases.

A spec written for an earlier version of the plugin has Problem, Goal and Scope sections and
`### Requirement:` headings. Rework it in your next edit to it: bring it to the template's layout
and this rubric, keeping what it says. Turn Problem and Goal into the Story and Scope into In scope
and Out of scope, number the requirements in their order, make each scenario an example table,
and turn each Verified by line into How we'll check. Anything the new checks need that the old
spec does not say, such as a first requirement stating the story's outcome, is a question for
the person, like any other gap. Keep each requirement's name, so plans that name it still match. A plan that names an
old spec cannot be signed off, nor built, until the spec has been reworked and accepted again, so
say so when you hand the spec over.

Then ask about what the draft or the review leaves open: say how many questions there are, ask only
the first (a conflict with another spec, or a decision the review says needs the person, comes
first), and do not mention any of the others anywhere in that reply, not even in passing or in a
report of what you or the review changed (they are in the spec); ask the next once it is settled,
playing back what you have understood. When you ask the person to settle a question in the
conversation, lay it out in four parts, so they can find your proposal at a glance: a bold line
naming it and its place in the count, such as "**Question 2 of 7: how often a failed pull is
retried**", where the first number counts the questions asked or settled in this conversation, this
one included, and the total adds those still open, so the first number only goes up, saying in one
line when an answer opens or settles others; the context it needs; a block quote holding a
"**Proposed:**" line with your answer, a line holding only `>`, and a "**Why:**" line with the
reason; and the question itself, last, in one line. If the person has
said not to ask now, give the count and leave the questions in Open questions. Settle each answer
before moving on: if the person answers part of what you asked, take that part and ask again about
the rest, because silence is not agreement; if they ask what you think, recommend something and wait
for them to accept it. If they would rather not answer now, leave the rest in Open questions.

Never fill a gap with a guess, including who the Story is about, their situation and the outcome: if
the person has not told you, write only what you were told, without adding a purpose or detail of
your own, say the rest is not known yet and ask in Open questions. A default you would choose, such
as how a reply quotes the message it answers, is never written as a rule: it goes into Open
questions, with the default as the proposed answer. Write each open question as a heading, `### 1.
<what is to be settled>`, numbered in order, then the context it needs, then a block quote holding a
line starting `> **Proposed:**` with the answer you would choose, then a line holding only `>`, then
a line starting `> **Why:**` with the reason, so the person can find the proposal at a glance and
accept it in a word
or give another. Each question holds one proposal, so a question with two answers is two questions,
and a plugin hook refuses Open questions laid out any other way. Where only the person can know the
answer, "Proposed:" says what would settle it instead, never a guess. Who the Story is about is such
a question (rubric check 14). Words whose meaning is plain from the conversation or the product,
such as "reply" in an email tool, are settled from that context, not asked about. Use only people
the person named, anywhere in the spec; example values such as `user@example.com` need no name. An
unknown goes into Open questions, worded so it can be answered. When the person names how something
should be built (a library, a service, a named bucket or database, a design), keep the behaviour it
serves and leave the choice out of every section, even when they state it as settled: the spec
should still hold if the choice changes, and tell the person you left it out. If it is already
decided, suggest recording it as an ADR (architecture decision record); if not, suggest deciding
it in one. Never ask a question whose answer is a technical choice, nor make it an open question:
say it belongs in an ADR, since a spec says what the product does, never how it is built. When an
unknown can only be settled by trying something, suggest a spike: a throwaway
experiment. When the person wants the spec to refer to the brief, another spec, an ADR, a plan or a
spike record, by hyperlink, path or title, leave it out (rubric check 11) and tell them why: that
document can change or be deleted without this spec being touched, so the reference would go stale.
Material they hand over that is not a web page, such as a requirements document or notes, is drawn
on but never referred to (rubric check 11): state what matters from it in the spec's own words, and
tell them it can change or vanish without the spec being touched.

Add only behaviour the person asked for or agreed to. A case they have not covered, such as who
may not use the feature, what happens on an error, or what happens when a rule's condition does
not hold, is an open question, not a rule you choose: a rule for paid invoices says nothing
about unpaid ones. For each requirement, ask yourself what happens when it cannot be met, such as
when a service it needs cannot be reached, and unless the person has said, make that an open
question. Write each requirement as rubric checks 5 to 8 describe: a numbered heading, one EARS
rule about something someone can see, example tables that add concrete cases, and How we'll
check.

Add a section beyond the template's, such as "Security", only when the person asks for one, and
place it as rubric check 1 says.

## Status

The `status:` frontmatter says whether the person has accepted the spec's text: `Draft 📝` or
`Accepted 👍`, written exactly so, word first, then its emoji. It describes the document, never the software:
whether the software meets the spec is found by checking the software against it. A status written as a bare word, or with its
emoji in front as earlier versions of the plugin wrote it, is written so in your next edit.

The frontmatter's `date:` is the day the status last changed, written YYYY-MM-DD: give a new
document today's date, set it to today's date in the same edit as every status change, and never
change it otherwise. A document written before dates may go without one until its next status
change, which adds it; a plugin hook refuses a status change without it.

- Write new and changed specs as `Draft 📝`. Changing a spec that is `Accepted 👍` returns it to
  `Draft 📝`, because what was accepted no longer matches: set the status to `Draft 📝` first, as a
  plugin hook refuses any other change to such a spec. A spec still holding `Ready to build 🟢` or
  `Built ✅`, statuses specs had before, goes back to `Draft 📝` the same way.
- `Accepted 👍` is the spec's one move forward. Move the document forward only when the person
  explicitly says so about its text as it now stands, once the review below has ended on that text,
  by a full review or a check of what changed, with every question it raised answered or ignored,
  and once Open questions says "None.". Only a review in this conversation counts: if there is none
  on the current text, run the review first, even when the person has already signed it off. Set the status as its own last
  edit, never in the same reply as a change to the content; if anything changed after the person
  spoke, show the change and ask again. "Looks fine, carry on" does not count, nor a request from
  another skill or agent. Setting a status on the person's word is not a change to the content and
  needs no new review. `Accepted 👍` means the person agreed to this text, so
  agreement given before they saw it does not count, even a request to fix small things and carry
  on. If questions remain, say how many and leave the spec as `Draft 📝`.

## Review

Every spec is reviewed once, corrected once, and then the corrections are checked. The
sequence is fixed so it always ends with a clear result: further rounds of review find little
more, and each round of corrections brings new mistakes.

1. **Review.** When the spec is written, start two agents in the foreground, not in the
   background, both in one message so they run side by side: the `agentic:spec-reviewer` agent
   and the `agentic:language-checker` agent, which checks the wording. Give each this request, its
   first line exactly as shown, since a plugin hook reads that line to keep a copy of the spec
   as reviewed:

   ```
   Document: <the spec's full path>
   Review this spec.
   ```

   Give the document's full path on the `Document:` line, the one you wrote it to: the hook works
   out the document's repository from it, so the review reads the right one whatever folder you
   started in. If it refuses to start them, do what its reason says.
   Each reads everything else it needs itself. Wait for both reports before touching the spec.
   If both pass with nothing under Needs a person, go straight to handing over.
2. **Correct, once.** Read the rubric and the Plain words rule again, then correct only what
   the reports list: each failed check and each item under Other findings in the review report,
   and each finding in the wording report. A wording item under Needs a person, whose
   meaning only the person knows, is a decision like any other. A decision under Needs a person
   is not written into the spec: it becomes a question for the person, with the answer you would
   propose, never a guess written in as settled. Leave
   suggestions alone and change nothing else, since an edit beyond the reports is the likeliest
   way to break something. Wait until every edit has succeeded. If nothing in the reports was
   yours to correct, there is nothing to check: go straight to handing over.
3. **Check the corrections.** Start the `agentic:correction-checker` agent in the foreground with
   this request, and add nothing to it: the hook attaches both reports and the spec as
   reviewed, word for word.

   ```
   Document: <the spec's full path>
   Check the corrections.
   ```

   If the hook refuses to start it, do what its reason says. If the check fails, change
   the spec no further: show the person the check's report, whose findings become questions, as
   below. Do not review or correct again; what happens next is their call.

After the sequence, edit the spec only as the person's answers say, or when they ask.

Whether the check passed or failed, end with the hand-over. It is what the person acts on, so make
it hard to miss anything. Show the person each document you wrote or changed: if the app you run in
can show them a file in a viewer, use it, and show a fresh copy after each change if what it shows
is a copy; always name each one's full path; never send them to a code-hosting site to read it. Give
them the review and wording reports and the check's report, if there was one, leaving out the
decisions they list for the person. When the review found a conflict with another spec, name that
spec and the rule that conflicts, since the spec itself cannot refer to it, so this reply is the
only place the person learns of it. Then say how many questions there are: its open questions, the
decisions the reports list and any correction the check found not made or broken. Say you will take
them one at a time, rather than asking whether to, and ask the first only, as a single question,
giving any examples as possible answers rather than further questions; if the person has said not to
ask now, ask nothing. Name the count only, not the items: each comes up when you reach it. List the
reviewers' suggestions separately, as optional: they never hold the spec back. Leave committing
to them.

Put each question to the person one at a time, by the asking rule: open questions, decisions for the
person and what a check finds. Offer four choices on your question tool: "Accept" your proposal, "My
own answer", "Ignore" and "Defer"; where you have none, end it with this line, word for word, since
a plugin hook looks for it to keep the answer: "Accept, give your own answer, ignore or defer?". If
the person has said not to ask now, or stops, defer the questions left.

Accept and My own answer write the answer in as the person gave it, removing the question from Open
questions if it is there; Ignore writes nothing and removes it; Defer leaves it there, or writes it
there with its proposal. Nothing else is written into Open questions. An ignored fault you cannot
fix leaves the document as it is: say which rubric check it fails.

When a round of questions ends and anything was written in, start the `agentic:correction-checker`
agent again with the same request: the hook attaches the text as last checked and the answers, so it
checks only what changed. Put what it raises to the person the same way. Never run a full review for
answers.

Once nothing is left to ask, the last question offers the next status, where there is one, one more
full review, or stopping; while any question is deferred, only the last two. Run a full review again
only when the person asks, after their own change, on a document rewritten to a new layout, or in a
new conversation.
