---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-04
---

# Record a spike's runs only through a script that writes them into the record

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. Its
`/spike` skill, a set of instructions Claude follows for one kind of task, settles a question by
a throwaway experiment, and writes it up as a spike record in `docs/spikes/`: the question, the
result that would answer it, the experiment's code, the output of every run, and the answer.
The answer rests only on what the runs produced, so the runs in the record must be exactly what
the experiment printed. A person who doubts the answer reads the runs, and the reviewer agent, a
separate instance of Claude that checks the record, judges the answer against them.

The record's other rules, such as which statuses follow which and that nothing may refer to a
spike record, are lifecycle rules in `docs/lifecycle.md`. This record holds one decision: how a
run reaches the record.

## Considered Options

- **Claude runs the experiment and copies its output into the record.** Rejected: when a model
  copies text, it sometimes rewords it without saying so. ADR 0011 (an architecture decision
  record, a document that records one technical decision and why it was made) records the
  measurement: with Sonnet, a Claude model, as the agent writing a document, 2 of 30 copied
  reports changed a line. A changed line in a run's
  output could turn a failure into a success, and no later step could tell.
- **A hook on Claude's shell commands that saves the output of each experiment.** A hook is a
  script Claude Code runs automatically at set moments. Rejected: a hook sees every command
  Claude runs and can't tell an experiment from any other, so it would either miss runs or save
  commands that aren't runs.
- **A script that is the only way to run an experiment.** The skill runs
  `skills/spike/scripts/spike.py` once per run. It refuses unless the record is `🟢 Ready to run`,
  builds a fresh working folder outside the repository from the record alone, runs the
  experiment's command there, and appends the run to the record's Runs section itself: when and
  where it ran, a short hash of the code, and the output word for word, with the value of each
  named secret replaced by its name. The status hook of ADR 0005, which refuses document status changes
  the lifecycle does not allow, also refuses any change to Runs made with Claude's file-editing
  tools, so among those tools the script's writes are the only ones.

## Decision Outcome

Chosen option: a script that is the only way to run an experiment, because the output then
reaches the record without passing through a model, and every run starts from what the record
holds, so anyone can run it again from the record alone.

### Consequences

- Good: a run's output in the record is what the experiment printed, apart from secrets replaced
  by their names and very long output shortened, which the run says.
- Good: each run starts from a fresh copy built from the record, so nothing left over from an
  earlier run or from the person's working tree changes the result.
- Bad: Claude can still run the experiment's code some other way, such as with its own shell
  command; the skill tells it not to, and the reviewer agent's check of the finished record confirms that
  every result the answer uses is in Runs, though it can't tell how a run got there.
- Bad: Runs can still be changed by a shell command or by hand; as for every document the hook
  of ADR 0005 guards, no check catches that.
- Bad: a step only a person can do, such as trying something on their own phone, passes through
  Claude, which hands their words to the script; the run says it is their observation.

### Confirmation

Applies to: every run of every spike record.
Checked by: test. Unit tests of the script check that it refuses a record that is not
`🟢 Ready to run`, appends each run's output exactly, replaces secrets, and leaves the working tree
unchanged. Unit tests of the status hook check that it refuses any edit to Runs. Tests of the
skill on sample conversations check that runs are made only through the script.

## Open questions

- None.
