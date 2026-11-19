---
name: brief
description: Write or change the product brief, the one short document at docs/brief.md that says what the product is, who it is for, why it exists and how we will know it works. Use whenever someone wants to start a new product, write or update a brief, a product vision or a one-pager, or capture what the product is and for whom before any specs are written, even if they don't say "brief". Not for one feature or capability; that is a spec.
---

# Brief

The brief says what the product is, who it is for, why it exists and how we will know it works.
A product has one, at `docs/brief.md`, edited in place; git is its history. Specs are written
against it, one per capability, so the brief holds only what is true of the whole product.
It states what the person intends the product to be, so change it only when they say that intent
has changed, never to match a spec or an ADR. Changing the brief edits no other document: any spec
or ADR it now contradicts is for the person to settle, and `/audit` finds them.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it leaves less to correct. Write in plain words, as the Plain
words section of [the lifecycle page](../../docs/lifecycle.md#plain-words) says: a language
checker holds every document to it. A new brief starts from
[assets/template.md](assets/template.md). Read these with the Read tool, not the shell, so the
person is not asked to approve a command.

The template's frontmatter holds only `type: Brief`, which says what the document is. A brief
written before it has no frontmatter, so add the template's with your next edit. The title never
names the document's type, as "Spec:" or "ADR:" in front of it would: the frontmatter's `type:`
already says what it is.

Never rename a document once its review has started: the review hook keeps the review under the
document's path, so a renamed document's corrections can't be checked. If the name no longer fits,
say so to the person, who can rename it once the review has ended.

## What to read

The brief records what the person intends, which only they know. So draft from what they said in
this conversation and from what they point you to, such as a document, a link or notes. If
`docs/brief.md` exists, read it and change it rather than starting again; the documents it
already links to on the web count as pointed to. Don't read anything else on your own, not the README, the
code or a connected service: what a repository holds today can quietly pass for what the product
is meant to be. If something would help, ask first ("There's a README here; shall I read it?")
and read it only if they say yes.

## Shape it with the person

Usually the person has already talked the product through. Draft from that, carrying over every
fact they gave that the brief's sections hold, such as who does what; where the
conversation changed its mind, the latest word wins. Only when there is nothing to draw on, ask
what they are building and for whom first.

Write only what they said or showed you, as rubric check 8 describes. Where they haven't said something, write in its section
that it is not known yet, and ask them about it, each question asking one thing: "What do they do today, and how long does it take?" is two
questions. Write each open question as a heading, `### 1. <what is to be settled>`, numbered in
order, then the context it needs, then a block quote holding a line starting `> **Proposed:**` with
the answer you would choose, then a line holding only `>`, then a line starting `> **Why:**` with
the reason, so the
person can find the proposal at a glance and accept it in a word or give another. Each question
holds one proposal, so a question with two answers is two questions, and a plugin hook refuses Open
questions laid out any other way. Where only the person can know the answer, "Proposed:" says what
would settle it instead, never a guess. In a brief, an answer you would choose rests on something
the person said or showed, since the brief holds only what they intend (rubric checks 8 and 10);
where nothing does, say what would settle it, such as "tell me what support staff do today". When
they want the brief to refer to a spec, an ADR (architecture decision record), a plan or a spike
record, by hyperlink, path or title, leave it out (check 9) and tell them why: that document can
change or be deleted without the brief being touched, so the reference would go stale. Material they
hand over that is not a web page, such as a requirements document or notes, is drawn on but never
referred to (check 9): state what matters from it in the brief's own words, and tell them it can
change or vanish without the brief being touched. When they mention something that belongs to a
later stage (rubric checks 2 and 7), leave it out and tell them where it goes: how one capability
behaves goes in its spec, so suggest `/spec`; a technology or design they have decided goes in an
ADR, and one they have not becomes a question for them.

Add a section beyond the template's, such as "Safety and security", only when the person asks
for one, and place it as rubric check 1 says.

Then ask about what the draft or the review leaves open: say how many questions there are and ask
only the first, as one question rather than two joined together, with any examples given as possible
answers rather than further questions. When you ask the person to settle a question in the
conversation, lay it out in four parts, so they can find your proposal at a glance: a bold line
naming it and its place in the count, such as "**Question 2 of 7: how often a failed pull is
retried**", where the first number counts the questions asked or settled in this conversation, across every document, this
one included, and the total adds those still open, so the first number only goes up, saying in one
line when an answer opens or settles others; the context it needs; a block quote holding a
"**Proposed:**" line with your answer, a line holding only `>`, and a "**Why:**" line with the
reason; and the question itself, last, in one line.
With no question tool but a decision card, as in a Claude project thread, ask in words as the skill
says, then post it on a card offering the choices that need no typing, your proposal recommended.
Ask one question per reply, then end your turn until the person answers it, even when your
question tool or card returns at once.
The others wait, so leave them out of that reply entirely: describe the draft by what it says, never by
what it lacks ("nothing yet on who else is involved" names a question), and report what you or the
review changed without naming the gaps that remain. Ask the next once the first is settled, playing
back what you have understood. Settle each answer before moving on: take the part they answered and
ask again about the rest, because silence is not agreement. If the person has said not to ask now,
or would rather not answer, give only the count: no question and no list of what the questions
cover. An open question goes only when their answer is written into the brief.

## Review

When the brief is written, review it. At the review step, read the Review process section of
`${CLAUDE_PLUGIN_ROOT}/docs/lifecycle.md` and follow its steps, then its "Ending with your answers"
part, with the reviewer and requests below.

The reviewer is the `agentic:brief-reviewer` agent. Its request, which the
`agentic:language-checker` agent gets too:

```
Document: <the brief's full path>
Review this brief.
```

The check's request, to the `agentic:correction-checker` agent:

```
Document: <the brief's full path>
Check the corrections.
```

Correct by making the brief accurate, never by dropping or hedging what the person said.

Whether the check passed or failed, end with the hand-over. It is what the person acts on, so make
it hard to miss anything. Show the person each document you wrote or changed: if the app you run in
can show them a file in a viewer, use it, and show a fresh copy after each change if what it shows
is a copy; always name each one's full path; never send them to a code-hosting site to read it. Give
them the review and wording reports and the check's report, if there was one, leaving out the
decisions they list for the person. Then say how many questions there are: its open questions, the
decisions the reports list and any correction the check found not made or broken. Say you will
take them one at a time, rather than asking whether to, and ask the first only, as a single
question, giving any examples as possible answers rather than further questions; if the person has
said not to ask now, ask nothing. Name the count only, not the items: each comes up when you reach
it. List the reviewers' suggestions separately, as optional: they never hold the brief back. Leave
committing to them.
