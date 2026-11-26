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
| /build's steps | A new script reads the plan's requirements in order and adds the fixed steps |
| /audit's and /verify's steps[^av] | The documents their existing scripts already print |
| Fixed lists, such as the steps of a document review | The shared rules that [ADR 0062](0062-show-progress-checklist.md) sets up |
| When to update | A hook after each helper agent finishes; for /build, also the script that already runs before each requirement |

## Background

[ADR 0062](0062-show-progress-checklist.md) has long skill runs show a numbered list of steps and
update it as each step ends, but not where the list or the moment of each update comes from. The plugin already moves such work into
scripts and hooks.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Scripts list the steps; a hook after each helper agent prompts the update | Chosen | Same list every run, and prompts arrive at the steps that take longest |
| The agent writes the list and picks when to update | Rejected | Lists differ between runs and updates get skipped |
| The plan writes out the build's steps | Rejected | Repeats the plan's requirements, and the two can drift apart |
| A hook that updates the list itself | Rejected | A hook runs a shell command and cannot call the agent's tools |

## Consequences

- Good: the list and its numbering are the same every run, so "step 3 of 7" always matches.
- Good: prompts need no wording in the skill.
- Bad: a new hook runs after every helper agent and must do nothing where no list is shown.
- Bad: the agent can still skip an update, so test cases must check it.
- Bad: by the person's choice, this hook is first tried in a project thread at the build's trial.

## Out of scope

- Where and how progress shows in each place, which [ADR 0062](0062-show-progress-checklist.md) decides.
- Prompts during a long step that starts no helper agent, such as a slow test run.

## How we'll check

Applies to: listing the steps of a long skill run and prompting its updates.

1. Test: the new script prints a plan's requirements in order, then the fixed steps, numbered.
2. Test: the hook prompts an update after a helper agent finishes, and lets every other tool call through unchanged.
3. Test: the per-requirement script's output names the step's number out of the total.
4. Demonstration: the hook's note reaches the agent on the command line, desktop and a project thread.

## Open questions

None.

## Technical detail

**The build script.** It reads the plan's Specs section with the parsing `scripts/status_check.py` already has, one
requirement per nested line, and prints them numbered, then "Reviews of the code", "Corrections", "Check that the corrections
broke nothing" and "Give the person the work and reports".

**The hook.** A `PostToolUse` hook on the `Agent`, `Task` and `SubagentHandback` tools adds a note to the agent: if it
is showing progress, then once this helper agent's report is in, update the list, marking the step
that agent ran as done with a one-line summary. The note works whether the agent ran in the
foreground, where its report is already in, or in the background, where it comes later. Like `scripts/card_nudge.py`, its wording applies only where a list is shown, so a skill
with no list ignores it.

**Per requirement.** `skills/build/scripts/before_code.py`, which /build already runs before each
requirement, adds a line naming the step's number and the total.

**Where the hook pays off.** The long steps found across the skills are the build's requirements,
covered by the per-requirement script; reviews, correction checks and the agents of /audit and
/verify, all helper agents; and /spike's runs and /deploy's wait, which start none.

**Tried in each place, 2026-11-26.** A throwaway hook on the `Agent` and `Task` tools added the
note "the code word is PELICAN-42", and the agent quoted it back: on the command line, in a headless
Claude Code session, and on desktop, in a session the Claude app ran on a Mac. In a project thread, which
this hook was not tried in, the plugin's own hooks on these tools already run, which is how review
reports reach the correction checker, and its card hook adds the same kind of note after a reply.
There a helper agent's report arrives through `SubagentHandback`, so the note comes with the report
even for a background agent. On the Mac the helper agent ran in
the background although asked for the foreground, so the note came when it started, not when it
finished; the note's wording above covers that.

[^skill]: A skill is a set of instructions the agent follows for one step of the plugin, run as a command such as /build.
[^hook]: A plugin hook is a command Claude Code runs automatically at a set moment, such as after a tool call, whose output it passes to the agent.
[^helper]: A helper agent is a separate agent a skill starts for one task, such as a reviewer.
[^av]: /audit checks the code against each accepted document; /verify runs the product and checks it against each accepted spec.
