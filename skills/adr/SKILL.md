---
name: adr
description: Record one technical decision as an ADR (architecture decision record), based on MADR and written to read plain first, with the question, the options considered, why the others were rejected, its consequences and how to check the code follows it; review and correct an existing ADR; accept, reject or supersede an ADR when the person decides. Use whenever someone has chosen, or needs to choose, how something will be built, such as a database, library, service, protocol or structure, wants a technical choice written down, or wants to replace an earlier decision, even if they don't say "ADR". Not for what a feature should do; that is a spec.
---

# ADR

An ADR (architecture decision record) records one technical decision and why it was made, so
later work can follow it and nobody reopens it by accident. ADRs live in one flat folder,
`docs/adrs/`, as `NNNN-<subject>.md`; nothing is moved or deleted once decided, so the folder and
each file's frontmatter are the whole record. Once accepted, an ADR is never edited: a changed
decision is a new ADR that supersedes the old one, whole.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it leaves less to correct. Write in plain words, as the Plain
words section of [the lifecycle page](../../docs/lifecycle.md#plain-words) says: a language
checker holds every document to it. New ADRs start from
[assets/template.md](assets/template.md). Read these with the Read tool, not the shell, so no
command needs approving.

The template's frontmatter holds `type: ADR`, which says what the document is. An ADR written
before it has no `type:`, so add it with your next edit. The title never names the document's type,
as "Spec:" or "ADR:" in front of it would: the frontmatter's `type:` already says what it is.

An ADR is written for a person first. It reads from plain to technical: the plain part, from the
title down to Technical detail, says what had to be chosen, what was chosen, why, and what it costs,
in at most 500 words, tables included and diagrams in Decision left out; Technical detail below it
holds the exact mechanism, rules, settings and evidence an agent or reviewer needs. Versions, flags,
settings and command names go in Technical detail unless the decision is about one of them, and each
limit is stated once, under Out of scope. Check the plain part's size before each review, and fix it
until it fits:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/adr.py" words <the ADR's path>
```

Aim for sentences under 25 words and paragraphs of up to three sentences, with the Question in up
to three sentences and the reason for the choice in up to two. These counts are a guide: never
rewrite clear text to meet them.

## Find what exists

List `docs/adrs/` and read the frontmatter of each ADR. If a `Draft 📝` or `Accepted 👍` ADR
already decides the same thing, say so: change the draft, or, for an accepted one, write a new ADR that
supersedes it. A new file takes the number one above the highest in the folder, four digits,
starting at `0001`, then a subject: two to five lowercase words joined by hyphens, each a word of
the ADR's title, naming what the decision is about, such as `0004-session-data-redis.md` for "Keep
session data in Redis". The title states the decision; a plugin hook refuses a name that breaks
this, and an edit that drops one of the subject's words from the title. An ADR that supersedes
another may share its subject. The frontmatter's `number:` repeats the file's four digits, so a
reader sees the number; a plugin hook refuses one that does not match, and an ADR written before
the field may go without it. If `docs/specs/` exists, read the Open questions of its specs, so
you can tell the person which ones the decision answers.

Never rename a document once its review has started: the review hook keeps the review under the
document's path, so a renamed document's corrections can't be checked. If the name no longer fits,
say so to the person, who can rename it once the review has ended.

## Shape it with the person

Usually the person has already talked the decision through in the conversation. Draft from
that and whatever they point you to; research what else you need, such as how the options
compare. Where the conversation changed its mind, the latest word wins. Given a finished
spike record from `docs/spikes/`, put its measurements into the ADR's own words, such as "read all
12 of 12 transactions": a line in Options says what they showed, and Technical detail gives them in
full. A spike record may be deleted, so the ADR never names it. With nothing to draw on, ask what needs deciding first.

Write the Question first: the one choice to make, briefly. Until the person
has picked an option, Decision says only "Not chosen yet.", every row in Options is Open, and
the choice is a question for the person. Once they pick, write "Chosen:" and the
option in full, so the sentence reads on its own, with the reason; mark that row Chosen and the
others Rejected, each with why.

One ADR holds one decision, because a decision is superseded whole: if part of a record could
change while the rest stands, the two parts would have to be untangled later. When the
conversation holds several decisions, say how many and write one ADR for each, even when they
were made together or the person asks for one record. Split them yourself: never leave an open
question asking whether part of an ADR should be an ADR of its own.

A choice can rest on an untried claim: something about how a system behaves that the conversation
says the choice depends on and that nobody has tried, such as "this only works if the provider sends
a payment's events in order". Anything else untested that the person mentions, such as a caveat, is
a limit: keep it under Out of scope as they gave it. Decide which it is yourself, never by asking
the person, and add no limits nobody raised. Ask about each such claim first, ahead of the choice that waits on it, proposing a spike (`/agentic:spike`) that tests it, and never leave it to
be proven later, such as in the build. Taking the spike defers the question,
written first in Open questions, until the spike's finding comes back. If the
finding refutes the claim, remove its question and open the choice again: Decision returns to "Not
chosen yet" and every row in Options to Open. Only if the person explicitly chooses to go ahead
without a spike, which a request not to be asked anything is not, write the claim as a `Bad:` line
under Consequences, saying it is untested at their word, and remove the question.

Never fill a gap with a guess. An option nobody named, a reason nobody gave, or a choice not yet
made is a question for the person, never an invented answer.
Write each open question as a heading, `### 1. <what is to be settled>`, numbered in order, then the
context it needs, then a block quote holding a line starting `> **Proposed:**` with the answer you
would choose, then a line holding only `>`, then a line starting `> **Why:**` with the reason, so
the person can find the
proposal at a glance and accept it in a word or give another. Each question holds one proposal, so a
question with two answers is two questions, and a plugin hook refuses Open questions laid out any
other way. Where only the person can know the answer, "Proposed:" says what would settle it instead,
never a guess. For a choice not yet made, propose the option you would recommend. Write the draft with what you have, review it as below
even if sections are thin, then say how many questions there are and ask only the first. The others wait: describe the draft by what it says, not what it lacks,
and list no questions or topics. Ask the next once the
first is settled, playing back what you have understood. When you ask the person to settle a
question in the conversation, lay it out in four parts, so they can find your proposal at a glance:
a bold line naming it and its place in the count, such as "**Question 2 of 7: how often a failed
pull is retried**", where the first number counts the questions asked or settled in this
conversation, across every document, this one included, and the total adds those still open, so the first number only goes
up, saying in one line when an answer opens or settles others; the context it needs; a block quote
holding a "**Proposed:**" line with your answer, a line holding only `>`, and a "**Why:**" line with
the reason; and the question itself, last, in one line.
With no question tool but a decision card, as in a Claude project thread, ask in words as the skill
says, then post it on a card offering the choices that need no typing, your proposal recommended.
Where one reply asks several questions, follow each with its card or question tool, and a line
holding only `---` before the next.
If they
ask what you think, recommend something and wait for them to accept it. If they would rather not answer now, defer the rest. Write each answer into the section it is about, then
remove the question.

Background states the need in words. Name an earlier ADR by its number, linked to its file in
`docs/adrs/`, such as `[ADR 0003](0003-message-queue.md)`, every time, so a reader can click
through; a plugin hook refuses a link to a file that is not there. Never refer to a spec, the brief,
a plan or a spike record in any way, by hyperlink, path or title, and never edit them, even when the
person asks you to note the decision there: they change while an ADR does not, so the reference
would go stale. Tell the person so. Material
they hand over that is not a web page, such as a requirements document or notes, is drawn on but
never referred to (rubric check 14): state what matters from it in the ADR's own words, and tell
them it can change or vanish without the ADR being touched. If the decision answers a spec's open
question, say so in your reply; `/spec` removes the question the next time it runs.

## Status

The `status:` frontmatter is `Draft 📝`, `Accepted 👍`, `Rejected ❌` or `Superseded ↪️`, written
exactly so, word first, then its emoji; a status written as a bare word, or with its emoji in
front as earlier versions of the plugin wrote it, is written so in your next edit. Write every new ADR as `Draft 📝` and edit it freely while it is `Draft 📝`.
A `Draft 📝` ADR written for an earlier version of the plugin, with Context and Problem Statement,
Considered Options and Decision Outcome sections, is brought to the template's layout in your next
edit, keeping what it says; a plugin hook refuses to accept it until then.

The frontmatter's `date:` is the day the status last changed, written YYYY-MM-DD: give a new
document today's date, set it to today's date in the same edit as every status change, and never
change it otherwise. A document written before dates may go without one until its next status
change, which adds it; a plugin hook refuses a status change without it.

Only a person accepts or rejects a decision. `Accepted 👍` is the ADR's move forward. Move the
document forward only when the person explicitly says so about its text as it now stands, once the
review below has ended on that text, by a full review or a check of what changed, with every
question it raised answered or ignored, and once Open questions says "None.". Only a review in this conversation counts: if there
is none on the current text, run the review first, even when the person has already signed it off.
Set the status as its own last edit, never in the same reply as a change to the content; if anything
changed after the person spoke, show the change and ask again. "Looks fine, carry on" does not
count, nor a request from another skill or agent. Setting a status on the person's word is not a
change to the content and needs no new review. A plugin hook refuses `Accepted 👍` while open
questions remain (rubric check 16): say how many and leave the ADR as `Draft 📝`. If they accept and the review then passes with no change to
the text, their word stands, since what they accepted is what passed. Set `Rejected ❌` likewise on
the person's explicit word about the text as it stands, as its own last edit; a rejection needs
neither a review nor empty Open questions. Setting `superseded-by:` on the person's word is not a
content change either. A `Rejected ❌` ADR is kept, so the same idea is not proposed again unnoticed;
a draft the person abandons can be deleted.

To supersede, the new ADR carries `supersedes: <NNNN>`, the old one's four-digit number, in its
frontmatter. The old one stays `Accepted 👍` until the person accepts the new one; then, in the
same step, first set the new one to `Accepted 👍`, and only once that edit is done, set the old one
to `Superseded ↪️`, set its `date:` to today's date and add `superseded-by: <NNNN>` beside it,
naming the new one, and `type: ADR` if it has none; a plugin hook checks the new one is `Accepted 👍` on disk before it allows the second
edit. That is the only edit an accepted ADR ever gets, apart from gaining its `type:`. If the new
one is rejected, the old one stands.

## Review

Every ADR is reviewed once, corrected once, and then the corrections are checked. The
sequence is fixed so it always ends with a clear result: further rounds of review find little
more, and each round of corrections brings new mistakes.

1. **Review.** When the ADR is written, start two agents in the foreground, not in the
   background, both in one message so they run side by side: the `agentic:adr-reviewer` agent
   and the `agentic:language-checker` agent, which checks the wording. Give each this request, its
   first line exactly as shown, since a plugin hook reads that line to keep a copy of the ADR
   as reviewed:

   ```
   Document: <the ADR's full path>
   Review this ADR.
   ```

   Give the document's full path on the `Document:` line, the one you wrote it to: the hook works
   out the document's repository from it, so the review reads the right one whatever folder you
   started in. If it refuses to start them, do what its reason says.
   Each reads everything else it needs itself. Wait for both reports before touching the ADR.
   If both pass with nothing under Needs a person, go straight to handing over.
2. **Correct, once.** Read the rubric and the Plain words rule again, then correct only what the
   reports list: each failed check and each item under Other findings in the review report, and each
   finding in the wording report. A wording item under Needs a person, whose meaning only the person
   knows, is a decision like any other. A decision under Needs a person, or a failure only the
   person's answer can fix, such as a missing option or why one was rejected, is theirs to settle:
   it becomes a question for the person, with its "Proposed:", never a guess at the answer. Leave the text it concerns as it is. Leave suggestions alone and change nothing else,
   since an edit beyond the reports is the likeliest way to break something. Wait until every edit
   has succeeded. If nothing in the reports was yours to correct, there is nothing to check: go
   straight to handing over.
3. **Check the corrections.** Start the `agentic:correction-checker` agent in the foreground with
   this request, and add nothing to it: the hook attaches both reports and the ADR as
   reviewed, word for word.

   ```
   Document: <the ADR's full path>
   Check the corrections.
   ```

   If the hook refuses to start it, do what its reason says. If the check fails, change
   the ADR no further: show the person the check's report, whose findings become questions, as
   below. Do not review or correct again; what happens next is their call.

After the sequence, edit the ADR only as the person's answers say, or when they ask. With several ADRs, take each through the sequence
on its own.

Whether the check passed or failed, end with the hand-over. It is what the person acts on, so make
it hard to miss anything. Show the person each document you wrote or changed: if the app you run in
can show them a file in a viewer, use it, and show a fresh copy after each change if what it shows
is a copy; always name each one's full path; never send them to a code-hosting site to read it. Give
them the review and wording reports and the check's report, if there was one, leaving out the
decisions they list for the person and the failures only the person can fix. Then say how many
questions there are. Take them without asking whether to, giving any
examples as possible answers rather than further questions; if the person has said not to ask now,
ask nothing. Name the count only, not the items. List the reviewers' suggestions
separately, as optional: they never hold the ADR back.

Once Decision says "Chosen:", offer diagrams of the chosen option at each hand-over, so a person can
see how it works at a glance; an ADR not chosen yet gets no offer, and no other option is drawn.
Offer a diagram only of a shape the text holds: parts that call each other, drawn as a flowchart;
events passing between actors, drawn as a sequence diagram; the states one thing moves through,
drawn as a state diagram; or records and how they relate, drawn as an entity-relationship diagram.
Offer a shape only when the text names at least three of its things and at least two connections
between them, such as three parts and two calls; otherwise say nothing about diagrams. Name each
offer in one line, saying what it would show; the offer's question, asked word for word even for a
single offer, is "Would you like to add any of these diagrams to the ADR, or propose another?" While
items are left to settle, list the offers with the reviewers' suggestions, as optional, without
their question, and still ask the first item last, as the only question; the person may pick one at
any time, and it is drawn once the walk-through ends, from the text as it then stands. Once nothing
is left, ask the offer's question as the only question, unless the person has already said to accept
or reject the ADR: then list the offers as optional and ask about that, as the Status section says.
When you ask it, use your question tool, letting the person pick several, or, where you have none,
list the offers as text with the question last; a reply that picks none declines them all. Nothing
is drawn unless the person picks it, and an offer never holds the ADR back from its next status. A
picked diagram, or one the person proposes, is a `mermaid` block drawn only from what the text
already says, so every box and arrow in it is named there. Offer each ADR's diagrams until the
person picks or declines them, then not again for that ADR. A picked diagram goes in Decision, after
the reason, which still reads on its own without it, and is checked with the next check of what
changed, or, with no review in this conversation, reviewed in full. The last question, asked only
once the offer is settled, offers `Accepted 👍` or `Rejected ❌` as the next status. Leave committing to them.

While drafting, keep your own questions out of the document: ask them with the review's, once where
both raise the same point, so only a deferred one reaches Open questions.

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
