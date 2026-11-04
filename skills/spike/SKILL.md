---
name: spike
description: Settle one unknown by a throwaway experiment, written up as a spike record in docs/spikes/ that holds the question, the result that would answer it, the experiment's code, every run's output and the answer; run the experiment only through the plugin's run script once the person signs off the design; review the design and the verdict; tell the person which spec or ADR the answer goes to. Use whenever someone wants to try something out, test an assumption, prototype, measure or check whether a library, service or approach works before settling a spec or an ADR, or to carry on with a spike record, even if they don't say "spike". Not for breaking work into tasks, for writing what a feature should do (a spec), or for recording a decision already made (an ADR), and never for building the product itself.
---

# Spike

A spike answers one question that thinking and reading can't, with the smallest experiment that
can answer it. Its write-up, the spike record, lives in `docs/spikes/YYYY-MM-DD-<question>.md`,
dated the day it is started, in one flat folder. What a spike produces is knowledge, not code: the
experiment's code lives only in the record and is never copied into the product.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it leaves less to correct. Write in plain words, as the Plain
words section of [the lifecycle page](../../docs/lifecycle.md#plain-words) says: a language
checker holds every document to it. New records start from
[assets/template.md](assets/template.md), whose Experiment lines the run script reads exactly.
Read these with the Read tool, not the shell, so the person is not asked to approve a command.

A spike runs in four steps: design, review the design, run, review the verdict. Work out from the
record's status where to start: no record or `📝 Draft` is design, `🟢 Ready to run` is running or
the verdict, and a `💡 Answered` or `❔ Not answered` record is finished and never changed again;
another try at its question is a new record.

## Design

Sharpen the question with the person until one experiment can answer it. If they ask several,
say how many there are, take the first, and leave the rest for later records. Where the question
comes from a spec's or an ADR's Open questions, read that document; the record may name it, and
nothing else.

Then write, with the person, the Question, What would answer it, the Experiment and the Code,
from the template, with the template's comments removed and Answer, Surprises, Where it goes and
Runs left empty. What would answer it is fixed before any run, so a result seen later can't change
what counts as success. Documentation helps design the experiment but never answers the
question, so the experiment must actually exercise the thing asked about.

- **Experiment.** Say what it does and why that answers the question, then fill in the template's
  lines. A result that can vary, such as anything over a network, anything timed or anything that
  calls an AI model, runs several times; say why the count is enough. Name in advance any result
  that would end the runs early, such as a crash showing the approach can't work.
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

Write every new record as `📝 Draft`; then run the design review.

## Run

Only a `🟢 Ready to run` record runs, and only through the run script, which writes each run into
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

- **The experiment itself is at fault,** for example it crashes for a reason the Experiment doesn't
  name: correct the Code, tell the person what you changed, and run the corrected code the full
  number of times. Earlier runs stay in Runs but no longer count.
- **A step only the person can do:** ask them to do it, then pass their answer unchanged:
  `python3 "${CLAUDE_SKILL_DIR}/scripts/spike.py" run <path> --data "${CLAUDE_PLUGIN_DATA}" --observation "<their words>"`.
- **A secret is not set:** the script records that it did not run. Tell the person how to set it
  in Claude Code's environment, and that otherwise the spike ends `❔ Not answered`.
- **The experiment can't run or settles nothing:** stop running; the verdict says so.

Changing the Question, What would answer it or the Experiment of a `🟢 Ready to run` record
returns it to `📝 Draft` in the same edit, for a new design review and sign-off; that is possible
only before the first run. After it they can't change: a different question or experiment is a
new record.

## Verdict

Once the runs are done, write:

- **Answer:** Yes, No, or Yes provided that a stated condition holds, comparing the runs of the
  latest code, by run number, with What would answer it. Nothing else is evidence. If the runs
  settled nothing, say what was learned and what is still unknown: the spike is `❔ Not answered`.
- **Surprises:** what the runs showed that the question didn't ask, or "None."
- **Where it goes:** a fact goes to the spec, a choice between ways of building something to an
  ADR, each named by its title if one exists in `docs/specs/` or `docs/adrs/`, or "Nothing".

Never edit a spec or an ADR yourself: whoever looks after it takes the answer there with `/spec`
or `/adr`, stating the evidence in that document's own words, since nothing may refer to a spike
record. Then run the verdict review.

## Status

The `status:` frontmatter is `📝 Draft`, `🟢 Ready to run`, `💡 Answered` or `❔ Not answered`,
written exactly so, emoji first. Only the person moves a record forward: set `🟢 Ready to run`
when they sign off the design, and `💡 Answered` or `❔ Not answered` when they confirm the
verdict, each only when they explicitly say so about the text as it now stands, after the review
ended with a pass on that text and Open questions says "None.". Only a review in this conversation
counts: if there is none on the current text, run it first. Set the status as its own last edit,
never in the same reply as a change to the content; "looks fine, carry on" doesn't count, nor a
request from another skill or agent. A plugin hook refuses status changes that break these rules;
if it refuses one, tell the person why.

## Review

A record is reviewed twice, each time once, corrected once, and then the corrections are checked:
the design before `🟢 Ready to run`, the verdict before it is finished. The sequence is fixed so it
always ends with a clear result.

1. **Review.** Start two agents in the foreground, not in the background, both in one message so
   they run side by side: the `sdlc:spike-reviewer` agent and the `sdlc:language-checker` agent.
   Give each this request, its first line exactly as shown, since a plugin hook reads that line to
   keep a copy of the record as reviewed, and its second naming the review:

   ```
   Document: <the record's path>
   Review this spike record's design.
   ```

   For the verdict, the second line is `Review this spike record's verdict.` Ask the language
   checker to leave out the Code and Runs, which are the experiment's own text. Wait for both
   reports before touching the record. If both pass with nothing under Needs a person, go
   straight to handing over.
2. **Correct, once.** Read the rubric and the Plain words rule again, then correct only what the
   reports list: each failed check and each item under Other findings in the review report, and
   each finding in the wording report. A decision only the person can make, such as what result
   counts as success, becomes an entry in Open questions, never a guess: leave the text it
   concerns as it is. Leave suggestions alone and change nothing else. Wait until every edit has
   succeeded. If nothing was yours to correct, go straight to handing over.
3. **Check the corrections.** Start the `sdlc:correction-checker` agent in the foreground with
   this request, and add nothing to it: the hook attaches both reports and the record as reviewed.

   ```
   Document: <the record's path>
   Check the corrections.
   ```

   If the hook refuses to start it, do what its reason says. If the check fails, stop: change the
   record no further, and show the person the check's report. Do not review or correct again.

When the person changes the record or asks you to, run the sequence again on the changed text.
Setting a status on the person's word needs no new review.

End with the hand-over. Give the person the record's path, the review and wording reports and the
check's report, if there was one, leaving out the decisions they list, which are now in Open
questions. Say how many items must be settled before the record can move on: its open questions,
plus any correction the check found not made or broken. Say you will take them one at a time and
ask the first only, as a single question; name the count only, not the items. List the
reviewers' suggestions apart, as optional. Once nothing is left, ask the person to sign off the
design, or to confirm the verdict, naming the status it would get. After the verdict, tell them
which spec or ADR to take the answer to next. Leave committing to them: to hand an unfinished
spike to a teammate, they commit the record.
