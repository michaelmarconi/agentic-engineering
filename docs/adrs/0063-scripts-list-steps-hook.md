---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0063
status: Draft 📝
date: 2026-11-26
---

# Scripts list the steps of a long run and a hook prompts each progress update

## Question

How does a skill[^skill] get the list of steps it shows, and the moment to update it, the same way
every run?

## Decision

Chosen: the steps come from scripts or fixed written lists, never from the agent's own reading,
and a plugin hook[^hook] prompts the agent to update its progress each time a helper agent[^helper]
finishes, because most long steps are a helper agent's run and a fixed source gives the same list
every time. The agent still makes each update and writes its summary.

| Part | Where it comes from |
| --- | --- |
| /build's steps | A new script reads the plan's requirements in order, reusing the status hook's parsing, then adds the fixed steps |
| /audit's and /verify's steps[^av] | The documents their existing scripts already print |
| Fixed lists, such as the steps of a document review | The "Showing progress" rules that [ADR 0062](0062-show-progress-checklist.md) sets up |
| When to update | A hook after each helper agent finishes; for /build, also the script that already runs before each requirement |

## Background

[ADR 0062](0062-show-progress-checklist.md) has long skill runs show a numbered list of steps and
update it as each step ends, but not where the list or the moment of each update comes from. The plugin already moves such work into scripts and hooks, such as one that reminds the agent to
post a question on a card.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Scripts list the steps; a hook after each helper agent prompts the update | Chosen | Same list every run, and prompts arrive at the steps that take longest |
| The agent writes the list and picks when to update | Rejected | Lists differ between runs and updates get skipped |
| The plan writes out the build's steps | Rejected | Repeats the plan's requirements, and the two can drift apart |
| A hook that updates the checklist itself | Rejected | A hook runs a shell command and cannot call the agent's tools |

## Consequences

- Good: the list and its numbering are the same every run, so "step 3 of 7" always matches.
- Good: prompts arrive without the skill's wording saying when.
- Bad: a new hook runs after every helper agent and must do nothing where no list is shown.
- Bad: the agent can still skip an update, so test cases must check it.

## Out of scope

- Where and how progress shows in each place, which [ADR 0062](0062-show-progress-checklist.md) decides.
- Prompts during a long step that starts no helper agent, such as a slow test run.

## How we'll check

Applies to: listing the steps of a long skill run and prompting its updates.

1. Test: the new script prints a plan's requirements in order, then the fixed steps, numbered.
2. Test: the hook prompts an update after a helper agent finishes, and lets every other tool call through unchanged.
3. Test: the per-requirement script's output names the step's number out of the total.
4. Demonstration: a recorded build test case shows the list updated after each step.

## Open questions

None.

## Technical detail

**The build script.** It reads the plan's Specs section the way `scripts/status_check.py` already does, one
requirement per nested line, and prints them numbered, then "Reviews of the code", "Corrections", "Check that the corrections
broke nothing" and "Give the person the work and reports".

**The hook.** A `PostToolUse` hook on the `Agent` and `Task` tools adds a note to the agent: if it
is showing progress, update the list now, marking the step that agent ran as done with a one-line
summary. Like `scripts/card_nudge.py`, its wording applies only where a list is shown, so a skill
with no list ignores it.

**Per requirement.** `skills/build/scripts/before_code.py`, which /build already runs before each
requirement, adds a line naming the step's number and the total.

**Where the hook pays off.** The long steps found across the skills are the build's requirements,
covered by the per-requirement script; reviews, correction checks and the agents of /audit and
/verify, all helper agents; and /spike's runs and /deploy's wait, which start none.

**Hooks in project threads.** The plugin's hooks run there too: while these ADRs were written in a
project thread, the plugin's link hook refused a link to an ADR not yet written.

[^skill]: A skill is a set of instructions the agent follows for one step of the plugin, run as a command such as /build.
[^hook]: A plugin hook is a command Claude Code runs automatically at a set moment, such as after a tool call, whose output it passes to the agent.
[^helper]: A helper agent is a separate agent a skill starts for one task, such as a reviewer.
[^av]: /audit checks the code against each accepted document; /verify runs the product and checks it against each accepted spec.
