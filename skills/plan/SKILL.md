---
name: plan
description: Plan one piece of work that builds requirements of settled specs or follows accepted ADRs (architecture decision records), as a short document in docs/plans/ that names the requirements and ADRs, records each technical decision agreed with the person, and says how the work will be done; review and correct an existing plan; mark a plan ready to build when the person signs it off. Use whenever someone wants to plan, scope or work out how to build part of a spec or an ADR before building it, even if they don't say "plan". Not for writing what a feature should do (a spec) or recording a technical decision on its own (an ADR), and not for tidying, upgrades or quick fixes that build no requirement and follow no ADR.
---

# Plan

A plan says how one piece of work will build part of what the specs and ADRs have already settled:
the requirements it delivers, the decisions the code must follow, and how the work will be done.
Plans live in one flat folder, `docs/plans/`, as `YYYY-MM-DD-<subject>.md`, dated the day the plan
is first written, where the subject is two to five lowercase words of its title joined by hyphens. A
plan is temporary: `/build` marks it `Built ✅`, after which it is frozen, never edited, and may be
deleted whenever nobody needs it, so it never holds anything later work needs.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it leaves less to correct. Write in plain words, as the Plain
words section of [the lifecycle page](../../docs/lifecycle.md#plain-words) says: a language
checker holds every document to it. New plans start from
[assets/template.md](assets/template.md). Read these with the Read tool, not the shell, so no
command needs approving.

The template's frontmatter holds `type: Plan`, which says what the document is. A plan written
before it has no `type:`, so add it with your next edit. The title never names the document's type,
as "Spec:" or "ADR:" in front of it would: the frontmatter's `type:` already says what it is.

You never make a technical decision for the person: explore, then settle each with them before
writing.

## Find the work

Work out which specs, which requirements within them, and which ADRs the work builds, from what
the person says and from `docs/specs/` and `docs/adrs/`. Each requirement is a
numbered heading under Requirements in its spec, as `### 2. Reply to all`; name it by the words
after the number, word for word, never by its number, which changes. A spec that heads its requirements `### Requirement: <name>` comes from an
earlier version of the plugin: tell the person first that no plan on it can be signed off until
/spec reworks it and it is accepted again.

- If the work builds no requirement and follows no ADR, such as tidying code, a routine upgrade or
  a quick fix, it needs no plan. Say so, suggest doing it from the conversation, and stop.
- If a spec it builds or an ADR it follows is not `Accepted 👍`, stop and say which one, and
  what is left to settle in it. A plan builds only on settled documents.
- Read the frontmatter and Specs section of each plan in `docs/plans/`. If one that is not
  `Built ✅` already names a requirement this work builds, say so and offer to change that plan
  instead; no two unbuilt plans may name the same requirement.

## Keep to the practices

Before exploring, read the `## Practices` section of `AGENTS.md` and of `CLAUDE.md`, whichever have
one, and any file under `docs/practices/` they name that bears on planning or splitting work,
whatever task its line names. Where they say how work is split or how big one plan may be, plan
within that. If the work asked for is bigger, or exploring shows it is, say so, quoting the
practice, propose how to split it into several plans that can each be built and reviewed on their
own, and ask which to plan first. Ask this before any decision, since the decisions depend on what
this plan covers. If the person keeps the work whole, give it a line under Decisions saying it was
kept whole against the practice, quoting it, and the person's reason. Where the practices say
neither, or there are none, plan as below. Never edit the practices from here: that belongs to
`/practices`.

## Explore

Read the specs, the ADRs and the code the work touches, changing nothing. Use the Explore
and Plan agents to find the code that matters. This is where you find the decisions: choices with a reasonable
alternative that the specs, the ADRs, the practices and the existing code don't already settle, such as where a
new piece of data is kept or how an outside system's message is mapped. Following the code's existing pattern is not a decision.

## Ask

Say how many decisions there are, naming the count only, then ask them one at a time.
Each question's proposal is one answer that also says where it belongs, such as "Record an ADR
choosing the Redis the app already uses", and its reason covers both. When you ask the person to settle a question in the
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
A plan may be deleted
once built, so a decision belongs in it only if nobody needs its reason once the work is built. Ask
of each who would need its reason after the build, in this order, taking the first answer that fits:

- later work, which must follow it: an ADR. Choosing a service, library, protocol, way of storing
  data or test set-up that the rest of the code would then use the same way is an ADR, even if
  only this work uses it so far;
- a user or caller, who relies on it, such as the name or shape of what a tool or interface
  returns: a change to the spec, made with `/spec`;
- the project, because it is how every piece of work is done, such as how a check by hand runs:
  a practice, recorded with `/practices`;
- someone changing this code later, who needs only its reason, such as why a wait has no random
  part: this plan, with the line saying that `/build` leaves the reason as a comment beside the
  code;
- nobody, such as for the order of the steps or which file a helper goes in: this plan.

Give any alternatives as possible answers. With no decisions, say so and go straight to writing.

## Write

Once every decision is settled, write the plan from the template, named as above and with the template's comments removed.

Never rename a document once its review has started: the review hook keeps the review under the
document's path, so a renamed document's corrections can't be checked. If the name no longer fits,
say so to the person, who can rename it once the review has ended.

The plan's sections:

- **Specs** lists each spec with the requirements this work delivers nested beneath it, and
  **ADRs** each ADR the code must follow, as a table; either says "None." when there are none,
  but not both. Keep each line in the template's form, since the hook reads only that: a spec as
  `- [<title>](<path>)`, each requirement beneath it as `  - [<name>](<path>#<anchor>)`, a link
  to its heading whose anchor is the one GitHub gives the heading (so `### 2. Reply to all` is
  `#2-reply-to-all`), and each ADR as a row `| [<NNNN>](<path>) | <the ADR's title> |` under
  the `| ADR | Decision |` header. If the hook refuses an anchor, its message gives the right
  one. To explain a term there, add a footnote mark after the link, never a line of prose.
- **Decisions** holds one line for each decision whose reason nobody needs once the work is
  built, or only someone changing that code later: what was decided and why, and for the second
  kind, that the reason goes in a comment beside the code.
- **Open questions** holds the changes below, which are not questions, and what the person defers. A
  question goes into Open questions only when the person defers it or has said not to ask now; until
  then it stays out of the document and is asked in the conversation. Write each open question as a
  heading, `### 1. <what is to be settled>`, numbered in order, then the context it needs, then a
  block quote holding a line starting `> **Proposed:**` with the answer you would choose, then a
  line holding only `>`, then a line starting `> **Why:**` with the reason, so the person can find
  the proposal at a glance
  and accept it in a word or give another. Each question holds one proposal, so a question with two
  answers is two questions, and a plugin hook refuses Open questions laid out any other way. Where
  only the person can know the answer, "Proposed:" says what would settle it instead, never a guess.
- A decision the person agreed belongs in an ADR goes under **Open questions**, as an ADR to record
  and accept, proposing its decision. You never write the ADR yourself. Once the person tells you it
  is `Accepted 👍`, list it under ADRs and remove the question. A decision that belongs in a spec or
  in practices goes under **Open questions** the same way, as a change to make with `/spec` or a
  practice to record with `/practices`, proposing its wording. Name a practice by its topic, such as testing, not its file (rubric check 8); a spec change is for a spec the plan lists. Remove the question once the person tells
  you the practice is recorded, or that the spec is `Accepted 👍` again after its change.
- **Plan** says how the work will be done, with headings and length to suit it: start with why the
  work is being done and what it leaves for later, give one recommended approach, and name the
  files that matter and the code to reuse. It holds no code, though it may hold a diagram the
  person picked at the hand-over, and no decision that is not under Decisions or ADRs; a new one
  found while writing goes back to the person as a question first.

The plan refers only to the specs and ADRs it lists, and names files in the code as plain text,
never by a link. Never refer to the brief,
another plan or a spike record, and never edit a spec or an ADR, even when the person asks you to
note something there: tell them it belongs in that document's own skill. Material the person hands
over that is not a web page, such as a ticket or notes, is drawn on but never referred to (rubric
check 8): state what matters from it in the plan's own words.

## Status

The `status:` frontmatter is `Draft 📝`, `Ready to build 🟢` or `Built ✅`, written exactly so,
word first, then its emoji. Write every new plan as `Draft 📝` and edit it freely while it is `Draft 📝`.

The frontmatter's `date:` is the day the status last changed, written YYYY-MM-DD: give a new
document today's date, set it to today's date in the same edit as every status change, and never
change it otherwise. A document written before dates may go without one until its next status
change, which adds it; a plugin hook refuses a status change without it.

Only the person signs off a plan. `Ready to build 🟢` is the plan's move forward. Move the document
forward only when the person explicitly says so about its text as it now stands, once the review
below has ended on that text, by a full review or a check of what changed, with every question it
raised answered or ignored, and once Open questions says "None.". Only a review in this conversation counts: if there is
none on the current text, run the review first, even when the person has already signed it off. Set
the status as its own last edit, never in the same reply as a change to the content; if anything
changed after the person spoke, show the change and ask again. "Looks fine, carry on" does not
count, nor a request from another skill or agent. Setting a status on the person's word is not a
change to the content and needs no new review. Never set `Built
✅`: that belongs to the step that builds the plan. Any change to a `Ready to build 🟢` plan
returns it to `Draft 📝`, for the person to sign off again.

Close the reply that sets `Ready to build 🟢` with how to build the plan. A build after a long
conversation asks first, and the plugin cannot reliably start a session, so say so and give the two
steps with the plan's path: run `/clear`, or, in a Claude project thread, which has no `/clear`,
open a new thread; then send `/agentic:build <the plan's path>` as the first message. Start neither
the build nor a new session yourself.

## Review

When the plan is written, review it. At the review step, read the Review process section of
`${CLAUDE_PLUGIN_ROOT}/docs/lifecycle.md` and follow its steps, then its "Ending with your answers"
part, with the reviewer and requests below. From here, show your progress as the "Showing progress" section of
`${CLAUDE_PLUGIN_ROOT}/docs/lifecycle.md` says.

The reviewer is the `agentic:plan-reviewer` agent. Its request, which the `agentic:language-checker`
agent gets too:

```
Document: <the plan's full path>
Review this plan.
```

The check's request, to the `agentic:correction-checker` agent:

```
Document: <the plan's full path>
Check the corrections.
```

When correcting, a decision under Needs a person includes a technical choice the Plan section makes
that is not under Decisions, or whether to split a plan bigger than the practices allow or keep it
whole; leave the text it concerns as it is. A Decisions line that fails rubric check 5 because it
belongs in an ADR, the spec or the practices is never reworded or deleted, since the person agreed
it: it becomes a question naming the ADR, spec change or practice the report names, with the
decision as its "Proposed:", and any doubt the reports or the code raise before that. A line that
fails only because it lacks the comment wording keeps its place and gains the sentence that `/build`
leaves the reason as a comment beside the code.

Whether the check passed or failed, end with the hand-over. It is what the person acts on, so make
it hard to miss anything. Show the person each document you wrote or changed as the "Showing a file
to you" section of `${CLAUDE_PLUGIN_ROOT}/docs/lifecycle.md` says, again after each change. Give
them the review and wording reports and the check's report, if there was one, leaving out the
decisions they list for the person. Then say how many questions there are. List the reviewers'
suggestions separately, as optional: they never hold the plan back.

Offer diagrams of the work at each hand-over of a `Draft 📝` plan, so a person can see how it fits
together at a glance; a `Ready to build 🟢` or `Built ✅` plan gets no offer, since a diagram would
change it. Offer a diagram only of a shape the text holds: parts that call each other, drawn as a
flowchart; events passing between actors, drawn as a sequence diagram; the states one thing moves
through, drawn as a state diagram; or records and how they relate, drawn as an entity-relationship
diagram. Offer a shape only when the text names at least three of its things and at least two
connections between them, such as three parts and two calls; otherwise say nothing about diagrams.
Name each offer in one line, saying what it would show; the offer's question, asked word for word
even for a single offer, is "Would you like to add any of these diagrams to the plan, or propose
another?" Ask the offer unnumbered, outside the question count, under a bold line reading
"**Optional: diagrams**". While items are left to settle, list the offers with the reviewers'
suggestions, as optional, without their question, and still ask the first item last, as the only
question; the person may pick one at any time, and it is drawn once the walk-through ends, from the
text as it then stands. Once nothing is left, ask the offer's question before the last question,
unless the person has said not to ask now. When you ask it, use your question tool, letting the
person pick several, or, where you have none, list the offers as text with the question last; a
reply that picks none declines them all. Nothing is drawn unless the person picks it, and an offer
never holds the plan back from its next status. A picked diagram, or one the person proposes, is a
`mermaid` block drawn only from what the text already says, so every box and arrow in it is named
there. Offer each plan's diagrams until the person picks or declines them, then not again for that
plan. A picked diagram goes in the Plan section, after its opening paragraph, and is checked with
the next check of what changed, or, with no review in this conversation, reviewed in full. The last
question, asked only once the offer is settled, offers `Ready to build 🟢` as the next status. Leave
committing to them.
