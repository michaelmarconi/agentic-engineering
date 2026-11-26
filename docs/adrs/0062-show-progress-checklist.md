---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0062
status: Accepted 👍
date: 2026-11-26
---

# Show progress of long skill runs on each place's task checklist, written once on the lifecycle page

## Question

While a skill[^skill] works for minutes without needing the person, how does the person see which
step it is on and what each finished step found?

## Decision

Chosen: a skill that will work for more than a minute or two without the person puts its steps on
the task list its place shows live when that stretch starts, and updates it as each step ends,
with a one-line summary of what it found. One section of the lifecycle page[^lifecycle],
"Showing progress", says how in each of the three places the plugin runs, with a fallback, and each skill that has
such a stretch points to it. Technical detail names those skills and their steps. The places:

| Place | What the agent does |
| --- | --- |
| Claude Code command line | Fills the live step list Claude Code shows |
| Claude Code desktop | Fills the same list |
| Claude project thread[^thread] | Fills the checklist the app shows, through its tool |
| Fallback, with no such list | Prints the numbered steps, then one summary line as each step ends |

## Background

A project thread hides the agent's tool calls, so in a long skill run the person cannot tell working
from stuck. Elsewhere the person sees each step run, but not how many remain.
No plugin rule covers progress. [ADR 0055](0055-show-file-lifecycle-page.md) wrote a rule that
differs by place once, on the lifecycle page.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Each place's own task list, updated as each step ends | Chosen | Each place shows it live; a thread moves it to the newest point on each update |
| Text lines or replies after each step | Rejected | Nothing shows the whole list |
| A message with a progress bar after each step | Rejected | Repeats what the list shows |
| A drawn diagram of the steps | Rejected | Cramped for long runs |

## Consequences

- Good: in every place, the person sees which step a long run is on and what each found.
- Good: changing what one place does means editing one section.
- Bad: the rule relies on how Claude Code and the Claude app show their lists.
- Bad: while one long step runs, such as a slow test suite, the list stays still.

## Out of scope

- How the steps are listed and when the agent is prompted to update them, which [ADR 0063](0063-scripts-list-steps-hook.md) decides.
- Thread work that is not a skill run.
- Other places, such as editor extensions.

## How we'll check

Applies to: how every skill with a long stretch of unattended work shows its progress.

1. Inspection: the places appear only in the lifecycle page's "Showing progress" section.
2. Test: the check script fails a skill in Technical detail's table that does not point to the section.
3. Test: a build of a test project, run on the command line, updates the list after each step.
4. Demonstration: on desktop and in a project thread, a three-step build updates the list after each step.

## Open questions

None.

## Technical detail

**Telling the places apart.** The agent goes by the tools it has. A project thread gives it a
tool that posts the thread's checklist: it uses that, since it is what the person sees there.
Otherwise it uses Claude Code's task tools, `TaskCreate` and `TaskUpdate` (`TodoWrite` in older
versions). With none of these, it prints the numbered lines.

**The skills and their steps.** Each list is numbered, and a finished line reads
"✓ 2. Column order: 2 tests pass".

| Skill | Shown when | Steps |
| --- | --- | --- |
| /build | the checks before building pass | one per requirement, in plan order; reviews; corrections; check that the corrections broke nothing; give the person the work and reports |
| /audit | its script has listed the documents to check | one per spec[^spec] or ADR; recheck the findings; report |
| /verify | the person agrees the list | one per spec; report |
| Document review in /brief, /spec, /adr, /plan, /practices | the review starts | review; corrections; check that the corrections broke nothing; give the person the document and reports |
| /spike[^spike] | the run starts | one per run of the experiment; review of the experiment's result |
| /deploy | the person says yes | deploy; check, which can wait minutes to pass; reply |

**The project-thread list moves.** Each update moves the checklist to the newest point in the
thread.

Agents that run side by side, as in /audit, report together, so their lines change together.

**Evidence.** In a project thread on 2026-11-26, a checklist was posted, six long messages
followed, and then the checklist was updated: the person saw it leave its first place and appear at
the newest point.

[^skill]: A skill is a set of instructions the agent follows for one step of the plugin, run as a command such as /build.
[^thread]: A Claude project thread is a conversation inside a project on claude.ai, where the agent runs on a remote machine and the person sees only its replies, its checklist and the files it attaches.
[^lifecycle]: The lifecycle page is the plugin's one page of shared rules, which the agent is given at the start of a session in a repository that uses the plugin's way of building software.
[^spike]: A spike is a throwaway experiment that settles one unknown before a decision is made.
[^spec]: A spec is the document that says what one capability of the product should do.
