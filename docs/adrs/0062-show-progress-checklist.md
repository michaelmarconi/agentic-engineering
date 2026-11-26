---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0062
status: Draft 📝
date: 2026-11-26
---

# Show progress of long skill runs on a checklist, written once on the lifecycle page

## Question

While a skill[^skill] works for minutes without needing the person, how does the person see which
step it is on and what each finished step found?

## Decision

Chosen: a skill that will work for more than a minute or two without the person shows a numbered
list of its steps when that stretch starts, and updates it as each step ends, with a one-line
summary of what the step found. One section of the lifecycle page[^lifecycle],
"Showing progress", says how in each of the three places the plugin runs, and each skill that has
such a stretch points to it. Technical detail names those skills and their steps. The places:

| Place | What the agent does |
| --- | --- |
| Claude Code command line | Prints the list as text at the start, then one summary line as each step ends |
| Claude Code desktop | The same as the command line |
| Claude project thread[^thread] | Posts the list as the thread's checklist, which the app keeps per thread, and updates it after each step |

## Background

A project thread hides the agent's tool calls, so during a long skill run the person cannot tell a
working thread from a stuck one. Elsewhere the person sees each step run, but not how many remain.
No plugin rule covers progress today. [ADR 0055](0055-show-file-lifecycle-page.md) wrote a rule that differs by place once, on the
lifecycle page.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| A numbered checklist, updated as each step ends | Chosen | Each update moves it to the newest point in the thread, and it has no length limit |
| A reply message after each step | Rejected | Fills the thread, and nothing shows the whole list |
| A separate message with a progress bar, after each step | Rejected | Repeats what the checklist already shows |
| A drawn diagram of the steps | Rejected | Cramped for a long plan, and easy to lay out wrong |

## Consequences

- Good: in every place, the person sees which step a long run is on and what each step found.
- Good: changing what one place does means editing one section.
- Bad: the project-thread case relies on the Claude app moving an updated checklist to the newest point.
- Bad: while one step runs for a long time, such as a slow test suite, the list does not change.

## Out of scope

- How the steps are listed and when the agent is prompted to update them, which [ADR 0063](0063-scripts-list-steps-hook.md) decides.
- Thread work that is not a skill run.
- Places other than the three, such as the editor extensions.

## How we'll check

Applies to: how every skill with a long stretch of unattended work shows its progress.

1. Inspection: the places appear only in the lifecycle page's "Showing progress" section.
2. Test: the check script fails a skill named under Technical detail that lacks a line pointing to the section.
3. Demonstration: in a project thread, building a plan[^plan] of three requirements shows a checklist updated after each step.

## Open questions

None.

## Technical detail

**Telling the places apart.** A project thread gives the agent a tool that posts the thread's
checklist. Given none, the agent is on the command line or in desktop, and prints the list.

**The skills and their steps.** Each list is numbered, and a finished line reads
"✓ 2. Column order: 2 tests pass".

| Skill | Shown when | Steps |
| --- | --- | --- |
| /build | the checks before building pass | one per requirement, in plan order; reviews; corrections; check that the corrections broke nothing; give the person the work and reports |
| /audit | its script has listed the documents to check | one per spec or ADR; recheck the findings; report |
| /verify | the person agrees the list | one per spec; report |
| Document review in /brief, /spec, /adr, /plan, /practices | the review starts | review; corrections; check that the corrections broke nothing; give the person the document and reports |
| /spike | the run starts | one per run of the experiment; review of the experiment's result |
| /deploy | the person says yes | deploy; check, which can wait minutes to pass; reply |

Agents that run side by side, as in /audit, report together, so their lines change together.

**Evidence.** In a project thread on 2026-11-26, a checklist was posted, six long messages
followed, and then the checklist was updated: the person saw it leave its first place and appear at
the newest point.

[^skill]: A skill is a set of instructions the agent follows for one step of the plugin, run as a command such as /build.
[^thread]: A Claude project thread is a conversation inside a project on claude.ai, where the agent runs on a remote machine and the person sees only its replies, its checklist and the files it attaches.
[^lifecycle]: The lifecycle page is the plugin's one page of shared rules, which the agent is given at the start of a session in a repository that uses the plugin's way of building software.
[^plan]: A plan is a short document for one piece of work. It names the requirements the work builds, each a numbered rule from a spec, the document that says what one capability of the product should do.
