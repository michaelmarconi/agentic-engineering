---
name: plan
description: Plan one piece of work that builds requirements of settled specs or follows accepted ADRs (architecture decision records), as a short document in docs/plans/ that names the requirements and ADRs, records each technical decision agreed with the person, and says how the work will be done; review and correct an existing plan; mark a plan ready to build when the person signs it off. Use whenever someone wants to plan, scope or work out how to build part of a spec or an ADR before building it, even if they don't say "plan". Not for writing what a feature should do (a spec) or recording a technical decision on its own (an ADR), and not for tidying, upgrades or quick fixes that build no requirement and follow no ADR.
---

# Plan

A plan says how one piece of work will build part of what the specs and ADRs have already settled:
the requirements it delivers, the decisions the code must follow, and how the work will be done.
Plans live in one flat folder, `docs/plans/`, as `YYYY-MM-DD-<title>.md`, dated the day the plan is
first written. A plan is temporary: `/build` marks it `✅ Built`, after which it is frozen, never
edited, and may be deleted whenever nobody needs it, so it never holds anything later work needs. A
technical decision later work has to follow belongs in an ADR, not here.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it leaves less to correct. Write in plain words, as the Plain
words section of [the lifecycle page](../../docs/lifecycle.md#plain-words) says: a language
checker holds every document to it. New plans start from
[assets/template.md](assets/template.md). Read these with the Read tool, not the shell, so the
person is not asked to approve a command.

The template's frontmatter holds `type: Plan`, which says what the document is. A plan written
before it has no `type:`, so add it with your next edit. The title never names the document's type,
as "Spec:" or "ADR:" in front of it would: the frontmatter's `type:` already says what it is.

You never make a technical decision for the person. Explore first, settle every decision with
them one at a time, and only then write.

## Find the work

Work out which specs, which requirements within them, and which ADRs the work builds, from what
the person says and from `docs/specs/` and `docs/adrs/`. Each requirement is a
numbered heading under Requirements in its spec, as `### 2. Reply to all`; name it by the words
after the number, word for word, and never by its number, which changes when requirements are
added or removed. A plan written for an earlier version of the agentic plugin names requirements
as `  - Requirement: <name>` lines and ADRs as bullets; rewrite those sections in the template's
form with your next edit, since the hook refuses that layout at sign-off. A spec that heads its requirements `### Requirement: <name>` was written for an
earlier version of the agentic plugin: no plan can be signed off on it until it is reworked with
/spec and accepted again, so tell the person so before planning against it.

- If the work builds no requirement and follows no ADR, such as tidying code, a routine upgrade or
  a quick fix, it needs no plan. Say so, suggest doing it straight from the conversation, and stop.
- If a spec it builds or an ADR it follows is not `👍 Accepted`, stop and say which one, and
  what is left to settle in it. A plan builds only on settled documents, and you never change a spec or an ADR from here.
- Read the frontmatter and Specs section of each plan in `docs/plans/`. If one that is not
  `✅ Built` already names a requirement this work builds, say so and offer to change that plan
  instead; no two unbuilt plans may name the same requirement.

## Keep to the practices

Before exploring, read the `## Practices` section of `AGENTS.md` and of `CLAUDE.md`, whichever
have one, and any file under `docs/practices/` they name that bears on planning or splitting work,
whatever task its line names. Where they say how work is split or how big one plan may be, plan
within that. If the work asked for is bigger, or exploring shows it is, say so, quoting the
practice, propose how to split it into several plans that can each be built and reviewed on their
own, and ask which to plan first. Ask this before any decision, since the decisions depend on
what this plan covers. If the person keeps the work whole, give it a line under Decisions saying
it was kept as one plan against the practice, quoting the practice, and the person's reason.
Where the practices say neither, or there are none, plan as below. Never edit the practices from
here: that belongs to `/practices`.

## Explore

Read the specs, the ADRs and the code the work touches, changing nothing. Use Claude Code's
built-in helper agents: the Explore agent to find the code that matters, and the Plan agent to
think through how to build it. This is where you find the decisions: choices with a reasonable
alternative that the specs, the ADRs, the practices and the existing code don't already settle, such as where a
new piece of data is kept or how an outside system's message is mapped. Following a pattern the
code already uses is not a decision, and nor is anything a spec, an ADR or a practice already says.

## Ask

Tell the person how many decisions there are, naming the count only, not the decisions: each comes
up when you reach it. Then ask the first only, and wait for the answer. Each question gives your
proposed answer and where it belongs, with a reason for both. A plan may be deleted once built, so
a decision belongs in it only if nobody needs its reason once the work is built. Ask of each who
would need its reason after the build, in this order, taking the first answer that fits:

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

Give any alternatives as possible answers, not as further
questions, and end with a single question, such as whether they agree with your proposal. Ask the
next once the first is settled. If an answer adds or removes a decision, say so and give the new
count. With no decisions, say so and go straight to writing.

## Write

Only when every decision is settled, write the plan from the template, with today's date in its
file name and the template's comments removed:

- **Specs** lists each spec with the requirements this work delivers nested beneath it, and
  **ADRs** each ADR the code must follow, as a table; either says "None." when there are none,
  but not both. Keep each line in the template's form, since the hook reads only that: a spec as
  `- [<title>](<path>)`, each requirement beneath it as `  - [<name>](<path>#<anchor>)`, a link
  to its heading whose anchor is the one GitHub gives the heading (lowercased, every character
  but letters, digits, `_`, `-` and spaces dropped, each space made `-`, so `### 2. Reply to all`
  is `#2-reply-to-all`), and each ADR as a row `| [<NNNN>](<path>) | <the ADR's title> |` under
  the `| ADR | Decision |` header. If the hook refuses an anchor, its message gives the right
  one. To explain a term there, add a footnote mark after the link, never a line of prose.
- **Decisions** holds one line for each decision whose reason nobody needs once the work is
  built, or only someone changing that code later: what was decided and why, and for the second
  kind, that `/build` leaves the reason as a comment beside the code.
- **Open questions** holds whatever only the person can settle. Every open question ends with
  "Proposed:" and the answer you would choose, so the person can accept it in a word or give
  another; where only the person can know the answer, "Proposed:" says what would settle it instead,
  never a guess.
- A decision the person agreed belongs in an ADR goes under **Open questions**, as an ADR to record
  and accept, proposing its decision. You never write the ADR yourself. Once the person tells you it
  is `👍 Accepted`, list it under ADRs and remove the question. A decision that belongs in a spec or
  in practices goes under **Open questions** the same way, as a change to make with `/spec` or a
  practice to record with `/practices`, proposing its wording. Name a practice by its topic, such as
  testing, never by its file, since a plan refers to no file under `docs/` but specs and ADRs (rubric
  check 8); a spec change is for a spec the plan lists. Remove the question once the person tells
  you the practice is recorded, or that the spec is `👍 Accepted` again after its change.
- **Plan** says how the work will be done, with headings and length to suit it: start with why the
  work is being done and what it leaves for later, give one recommended approach, and name the
  files that matter and the code to reuse. It holds no code, though it may hold a diagram the
  person picked at the hand-over, and no decision that is not under Decisions or ADRs; a new one
  found while writing goes back to the person as a question first.

The plan refers only to the specs and ADRs it lists, and to the code. Never refer to the brief,
another plan or a spike record, and never edit a spec or an ADR, even when the person asks you to
note something there: tell them it belongs in that document's own skill. Material the person hands
over that is not a web page, such as a ticket or notes, is drawn on but never referred to (rubric
check 8): state what matters from it in the plan's own words.

## Status

The `status:` frontmatter is `📝 Draft`, `🟢 Ready to build` or `✅ Built`, written exactly so,
emoji first. Write every new plan as `📝 Draft` and edit it freely while it is `📝 Draft`.

The frontmatter's `date:` is the day the status last changed, written YYYY-MM-DD: give a new
document today's date, set it to today's date in the same edit as every status change, and never
change it otherwise. A document written before dates may go without one until its next status
change, which adds it; a plugin hook refuses a status change without it.

Only the person signs off a plan. `🟢 Ready to build` is the plan's move forward. Move the document
forward only when the person explicitly says so about its text as it now stands, once the review
below has ended with a pass on that text, from the review itself or from the correction check after
it, and once Open questions says "None.". Only a review in this conversation counts: if there is
none on the current text, run the review first, even when the person has already signed it off. Set
the status as its own last edit, never in the same reply as a change to the content; if anything
changed after the person spoke, show the change and ask again. "Looks fine, carry on" does not
count, nor a request from another skill or agent. Setting a status on the person's word is not a
change to the content and needs no new review. No hook checks that a review ran. Never set `✅
Built`: that belongs to the step that builds the plan. Any change to a `🟢 Ready to build` plan
returns it to `📝 Draft`, for the person to sign off again. A plugin hook refuses status changes that
break these rules; if it refuses one, tell the person why.

## Review

Every plan is reviewed once, corrected once, and then the corrections are checked. The sequence
is fixed so it always ends with a clear result: further rounds of review find little more, and
each round of corrections brings new mistakes.

1. **Review.** When the plan is written, start two agents in the foreground, not in the
   background, both in one message so they run side by side: the `agentic:plan-reviewer` agent and
   the `agentic:language-checker` agent, which checks the wording. Give each this request, its first
   line exactly as shown, since a plugin hook reads that line to keep a copy of the plan as
   reviewed:

   ```
   Document: <the plan's full path>
   Review this plan.
   ```

   Give the document's full path on the `Document:` line, the one you wrote it to: the hook works
   out the document's repository from it, so the review reads the right one whatever folder you
   started in. If it refuses to start them, do what its reason says.
   Each reads everything else it needs itself. Wait for both reports before touching the plan.
   If both pass with nothing under Needs a person, go straight to handing over.
2. **Correct, once.** Read the rubric and the Plain words rule again, then correct only what the
   reports list: each failed check and each item under Other findings in the review report, and each
   finding in the wording report. A wording item under Needs a person, whose meaning only the person
   knows, is a decision like any other. A decision under Needs a person, such as a technical choice
   the Plan section makes that is not under Decisions, or whether to split a plan bigger than the
   practices allow or keep it whole, becomes an entry in the plan's Open questions, with its
   "Proposed:", never a guess at the answer: leave the text it concerns as it is. A Decisions line
   that fails rubric check 5 because it belongs in an ADR, the spec or the practices is not reworded
   or deleted: move it from Decisions to Open questions, naming the ADR to record, the spec change
   to make with `/spec` or the practice to record with `/practices` that the report names, with the
   decision itself, as it stood under Decisions, as its "Proposed:". The person agreed that
   decision, so a correction never changes it: if the reports or the code give reason to doubt it,
   say so in the question's text, before "Proposed:". A line that fails only because it lacks the
   comment wording keeps its place and gains the sentence that `/build` leaves the reason as a
   comment beside the code. Leave suggestions alone and change nothing else, since an edit beyond
   the reports is the likeliest way to break something. Wait until every edit has succeeded. If
   nothing in the reports was yours to correct, there is nothing to check: go straight to handing
   over.
3. **Check the corrections.** Start the `agentic:correction-checker` agent in the foreground with
   this request, and add nothing to it: the hook attaches both reports and the plan as reviewed,
   word for word.

   ```
   Document: <the plan's full path>
   Check the corrections.
   ```

   If the hook refuses to start it, do what its reason says. If the check fails, stop: change the
   plan no further, and show the person the check's report. Do not review or correct again; what
   happens next is their call.

After the sequence, edit the plan only when the person asks. While you are walking through questions
with the person, do not review after each answer: run the sequence once when the walk-through ends,
either because no questions are left or because the person stops. A change the person makes or asks
for at any other time is reviewed once it is made.

Whether the check passed or failed, end with the hand-over. It is what the person acts on, so make
it hard to miss anything. Show the person each document you wrote or changed: if the app you run in
can show them a file in a viewer, use it, and show a fresh copy after each change if what it shows
is a copy; always name each one's full path; never send them to a code-hosting site to read it. Give
them the review and wording reports and the check's report, if there was one, leaving out the
decisions they list for the person, which are now in the plan's Open questions. Then say how many
items must be settled before the plan can be ready to build: its open questions, plus any correction
the check found not made or broken. Say you will take them one at a time, rather than asking whether
to, and ask the first only, as a single question, giving any examples as possible answers rather
than further questions; if the person has said not to ask now, ask nothing. Name the count only, not
the items: each comes up when you reach it. List the reviewers' suggestions separately, as optional:
they never hold the plan back.

Offer diagrams of the work at each hand-over of a `📝 Draft` plan, so a person can see how it fits
together at a glance; a `🟢 Ready to build` or `✅ Built` plan gets no offer, since a diagram would
change it. Offer a diagram only of a shape the text holds: parts that call each other, drawn as a
flowchart; events passing between actors, drawn as a sequence diagram; the states one thing moves
through, drawn as a state diagram; or records and how they relate, drawn as an entity-relationship
diagram. Offer a shape only when the text names at least three of its things and at least two
connections between them, such as three parts and two calls; otherwise say nothing about diagrams.
Name each offer in one line, saying what it would show; the offer's question, asked word for word
even for a single offer, is "Would you like to add any of these diagrams to the plan, or propose
another?" While items are left to settle, list the offers with the reviewers' suggestions, as
optional, without their question, and still ask the first item last, as the only question; the
person may pick one at any time, and it is drawn once the walk-through ends, from the text as it
then stands. Once nothing is left, ask the offer's question as the only question, unless the person
has said not to ask now, or has already said the plan is ready to build: then list the offers as
optional, and in that second case ask about it, as the Status section says. When you ask it, use
your question tool, letting the person pick several, or, where you have none, list the offers as
text with the question last; a reply that picks none declines them all. Nothing is drawn unless the
person picks it, and an offer never holds the plan back from its next status. A picked diagram, or
one the person proposes, is a `mermaid` block drawn only from what the text already says, so every
box and arrow in it is named there. Offer each plan's diagrams until the person picks or declines
them, then not again for that plan. A picked diagram goes in the Plan section, after its opening
paragraph, and is reviewed with the rest of the plan, or on its own if the walk-through has ended.
Once the offer is settled and nothing else is, ask whether the plan is ready to build. Leave
committing to them.
