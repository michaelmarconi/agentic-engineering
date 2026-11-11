---
name: spike
description: Settle one unknown by a throwaway experiment, written up as a spike record in docs/spikes/ that a person can read top-down, holding the hypothesis, the result that would confirm or refute it, the experiment's code, every run's output and the finding; run the experiment only through the plugin's run script once the person signs off the design; review the design and the verdict; tell the person which spec or ADR the finding goes to. Use whenever someone wants to try something out, test an assumption, prototype, measure or check whether a library, service or approach works before settling a spec or an ADR, or to carry on with a spike record, even if they don't say "spike". Not for breaking work into tasks, for writing what a feature should do (a spec), or for recording a decision already made (an ADR), and never for building the product itself.
---

# Spike

A spike settles one unknown that thinking and reading can't, by testing one hypothesis with the
smallest experiment that can confirm or refute it. Its write-up, the spike record, lives in
`docs/spikes/YYYY-MM-DD-<hypothesis>.md`,
dated the day it is started, in one flat folder. What a spike produces is knowledge, not code: the
experiment's code lives only in the record and is never copied into the product.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it leaves less to correct. Write in plain words, as the Plain
words section of [the lifecycle page](../../docs/lifecycle.md#plain-words) says: a language
checker holds every document to it. New records start from
[assets/template.md](assets/template.md), whose Experiment lines the run script reads exactly.
Read these with the Read tool, not the shell, so the person is not asked to approve a command.

The template's frontmatter holds `type: Spike`, which says what the document is. A spike record
written before it has no `type:`, so add it with your next edit. The title never names the
document's type, as "Spec:" or "ADR:" in front of it would: the frontmatter's `type:` already says
what it is.

A record is written for a person first. It reads from plain to technical: the plain part, from the
title down to Experiment, says what we expected, what we found and what happens next, in at most 600
words, tables included and `mermaid` diagrams left out; Experiment, Code and Runs below it hold
everything an agent or reviewer needs to check or repeat the experiment. Versions, settings, file
names and exact output go in Experiment unless the hypothesis is about one of them, and each limit
is stated once, under Out of scope. Check the plain part's size before each review, and fix it until
it fits:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/spike.py" words <the record's path>
```

A spike runs in four steps: design, review the design, run, review the verdict. Work out from the
record's status where to start: no record or `📝 Draft` is design, `🟢 Ready to run` is running or
the verdict, and a `💡 Confirmed`, `🚫 Refuted` or `❔ Not settled` record is finished and never
changed again; another try at its hypothesis is a new record.

## Design

Sharpen the person's question with them into one hypothesis, a claim one experiment can confirm
or refute, such as "the importer reads the bank's file as sent" for "can the importer read the
bank's file?". An open measurement becomes a claim with a threshold, such as "the search answers
in under 200 milliseconds for a million rows". If they raise several, say how many there are,
take the first, and leave the rest for later records. Where the question comes from a spec's or
an ADR's Open questions, read that document; the record may name it, and nothing else.

Then write, with the person, the design sections from the template: Hypothesis, How we'll know,
Out of scope, How the test works, Risks and safeguards, Experiment and Code, with the template's
comments removed and Finding, Next steps, Results, Surprises and Runs left empty. How we'll know
is fixed before any run, so a result seen later can't change what counts as success.
Documentation helps design the experiment but never settles the hypothesis, so the experiment
must actually exercise the thing in question.

- **How the test works.** Say in plain words what the experiment does, as a numbered list or a
  table of steps, and why that tests the hypothesis. A result that can vary, such as anything
  over a network, anything timed or anything that calls an AI model, runs several times; say why
  the count is enough.
- **Risks and safeguards.** When the experiment changes or reads anything real, such as a live
  account, real data, money or someone else's system, say each way it could do harm and what
  stops it, in plain words; otherwise write "None.".
- **Experiment.** The full method, the exact rules for what counts as confirmed or refuted, and
  every safeguard in detail, then the template's lines. Name in advance any result that would end
  the runs early, such as a crash showing the approach can't work.
- **Code.** Each code block names its file on its first line, such as `# file: check.py`. To try
  something in the product's own code, name the commit to start from and give the change as a
  `diff` block against it: the run script makes the copy, so never edit the product's files and
  never make a copy yourself. Read the product's code in the repository as you need.
- **Inputs.** Name every file or web address the code reads that the Code doesn't write. A path in
  the repository needs the commit to start from.
- **Secrets.** Name each secret by its environment variable only. The experiment reads it from
  Claude Code's environment: set before Claude Code started, or in a cloud session's environment
  settings. Never ask for a secret's value in the conversation, and never let code print, log or
  write one, in any form.
- **A step only the person can do,** such as trying something on their own phone, is a run they
  report: write `- Command: None.` when every run is theirs, and describe what they will do.

Anything only the person can settle, such as what result counts as success, goes into Open
questions. Every open question ends with "Proposed:" and the answer you would choose, so the person
can accept it in a word or give another; where only the person can know the answer, "Proposed:" says
what would settle it instead, never a guess.

Write every new record as `📝 Draft`, named for today's date and a few words naming the hypothesis;
then run the design review. Never rename a record once its review has started: the review is kept
under the record's path, so a renamed record can't have its corrections checked.

## Run

Asked to run a `📝 Draft` record, run its design review instead, even when the person asks to
skip it, and say the experiment runs once they sign off the reviewed design: the sign-off rests on
the review, and running first would let the results shape the hypothesis. Only a `🟢 Ready to run`
record runs, and only through the run script, which writes each run into
Runs word for word, so the record shows exactly what the experiment produced. Never run the
experiment's code any other way, never retype or summarise a result into the record, and never
edit Runs: a plugin hook refuses it. For each run:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/spike.py" run <the record's path> --data "${CLAUDE_PLUGIN_DATA}"
```

Give the shell command a 10-minute timeout: the script stops a run still going after 9 minutes
and records that. Run it once per call, as many times as `- Runs:` says, counting the runs already in Runs whose
code hash matches the latest code, so a resumed spike carries on where it stopped. After each run,
read its output: stop early only when it shows the result named under `- Stop early if:`. If the
script refuses, do what its reason says.

The run script writes the record itself, so read the record again after each run before you edit
it, and make sure each edit succeeded before the next run.

- **The experiment itself is at fault,** for example it crashes for a reason the Experiment doesn't
  name: correct the Code, tell the person what you changed, and run the corrected code the full
  number of times. Earlier runs stay in Runs but no longer count.
- **A step only the person can do:** ask them to do it, then pass their answer unchanged:
  `python3 "${CLAUDE_SKILL_DIR}/scripts/spike.py" run <path> --data "${CLAUDE_PLUGIN_DATA}" --observation "<their words>"`.
- **A secret is not set:** the script records that it did not run. Tell the person how to set it
  in Claude Code's environment, and that otherwise the spike ends `❔ Not settled`.
- **The experiment can't run or settles nothing:** stop running; the verdict says so.

Changing a design section of a `🟢 Ready to run` record, its Hypothesis, How we'll know, Out of
scope, How the test works, Risks and safeguards or Experiment, returns it to `📝 Draft` in the same
edit, for a new design review and sign-off; that is possible only before the first run. After it
they can't change: a different hypothesis or experiment is a new record.

## Verdict

Once the runs are done, write:

- **Finding:** Confirmed, Refuted or Not settled, followed by what was found, in full, so the
  sentence makes sense on its own, such as "Confirmed: the importer reads all 12 transactions of
  the bank's file as sent." Never a bare status word. Then up to three sentences comparing the
  runs of the latest code, by run number, with How we'll know, and pointing to Out of scope for
  its limits. Nothing but the runs is evidence. If the runs settled nothing, say what was learned
  and what is still unknown: the spike is `❔ Not settled`.
- **Next steps:** a fact goes to the spec, a choice between ways of building something to an
  ADR, and a finding that settles an ADR's open question to that ADR, each named by its title if
  one exists in `docs/specs/` or `docs/adrs/`, or "Nothing".
- **Results:** a table with a row for every run in Runs, with the columns Run (its number),
  Date, Outcome and Note (one line), then a sentence saying which runs count.
- **Surprises:** what the runs showed that the hypothesis didn't cover, or "None.". A limit the
  runs uncover goes here, since Out of scope is fixed once the design is signed off.

Never edit a spec or an ADR yourself: whoever looks after it takes the finding there with `/spec`
or `/adr`, stating the evidence in that document's own words, since nothing may refer to a spike
record. Check the plain part's size, then run the verdict review. The design is fixed by now, so
a verdict over the limit shortens its own sections, not the design's.

## Status

The `status:` frontmatter is `📝 Draft`, `🟢 Ready to run`, `💡 Confirmed`, `🚫 Refuted` or `❔ Not
settled`, written exactly so, emoji first. Only the person moves a record forward: `🟢 Ready to run`
when they sign off the design, and the status the Finding starts with when they confirm the verdict.
Move the document forward only when the person explicitly says so about its text as it now stands,
once the review below has ended with a pass on that text, from the review itself or from the
correction check after it, and once Open questions says "None.". Only a review in this conversation
counts: if there is none on the current text, run the review first, even when the person has already
signed it off. Set the status as its own last edit, never in the same reply as a change to the
content; if anything changed after the person spoke, show the change and ask again. "Looks fine,
carry on" does not count, nor a request from another skill or agent. Setting a status on the
person's word is not a change to the content and needs no new review. A plugin hook refuses status
changes that break these rules; if it refuses one, tell the person why.

The frontmatter's `date:` is the day the status last changed, written YYYY-MM-DD: give a new
document today's date, set it to today's date in the same edit as every status change, and never
change it otherwise. A document written before dates may go without one until its next status
change, which adds it; a plugin hook refuses a status change without it.

## Review

A record is reviewed twice, each time once, corrected once, and then the corrections are checked:
the design before `🟢 Ready to run`, the verdict before it is finished. The sequence is fixed so it
always ends with a clear result: further rounds of review find little more, and each round of
corrections brings new mistakes.

1. **Review.** Start two agents in the foreground, not in the background, both in one message so
   they run side by side: the `agentic:spike-reviewer` agent and the `agentic:language-checker` agent.
   Give each this request, its first line exactly as shown, since a plugin hook reads that line to
   keep a copy of the record as reviewed, and its second naming the review:

   ```
   Document: <the record's full path>
   Review this spike record's design.
   ```

   Give the document's full path on the `Document:` line, the one you wrote it to: the hook works
   out the document's repository from it, so the review reads the right one whatever folder you
   started in. If it refuses to start them, do what its reason says. For the verdict, the second
   line is `Review this spike record's verdict.` Ask the language checker to leave out the Code and
   Runs, which are the experiment's own text. Each reads everything else it needs itself. Wait for
   both reports before touching the record. If both pass with nothing under Needs a person, go
   straight to handing over.
2. **Correct, once.** Read the rubric and the Plain words rule again, then correct only what the
   reports list: each failed check and each item under Other findings in the review report, and each
   finding in the wording report. A wording item under Needs a person, whose meaning only the person
   knows, is a decision like any other. A decision only the person can make, such as what result
   counts as success, becomes an entry in Open questions, with its "Proposed:", never a guess: leave
   the text it concerns as it is. Leave suggestions alone and change nothing else, since an edit
   beyond the reports is the likeliest way to break something. Wait until every edit has succeeded.
   If nothing was yours to correct, go straight to handing over.
3. **Check the corrections.** Start the `agentic:correction-checker` agent in the foreground with
   this request, and add nothing to it: the hook attaches both reports and the record as reviewed.

   ```
   Document: <the record's full path>
   Check the corrections.
   ```

   If the hook refuses to start it, do what its reason says. If the check fails, stop: change the
   record no further, and show the person the check's report. Do not review or correct again; what
   happens next is their call.

While you are walking through questions with the person, do not review after each answer: run the
sequence once when the walk-through ends, either because no questions are left or because the
person stops. A change the person makes or asks for at any other time is reviewed once it is made.

End with the hand-over. Show the person each document you wrote or changed: if the app you run in
can show them a file in a viewer, use it, and show a fresh copy after each change if what it shows
is a copy; always name each one's full path; never send them to a code-hosting site to read it. Give
the person the review and wording reports and the check's report, if there was one, leaving out the
decisions they list, which are now in Open questions. Say how many items must be settled before the
record can move on: its open questions, plus any correction the check found not made or broken. Say
you will take them one at a time and ask the first only, as a single question; name the count only,
not the items. List the reviewers' suggestions apart, as optional. Once nothing is left, ask the
person to sign off the design, or to confirm the verdict, naming the status it would get. After the
verdict, tell them which spec or ADR to take the finding to next. Leave committing to them: to hand
an unfinished spike to a teammate, they commit the record.
