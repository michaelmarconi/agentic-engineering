---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0065
status: Draft 📝
date: 2026-11-27
supersedes: 0062
---

# Show progress on the checklist of each place the plugin runs, with a sub-step for each helper agent

## Question

During a long skill[^skill] run, how does the person see which step is under way, what each found,
and how far a step with several helper agents[^helper] has got?

## Decision

Chosen: a long skill run shows its numbered steps on the live task list of the place it runs in, updated as
each step ends with a one-line summary. While a step that starts more than one helper agent runs,
its line is replaced by one numbered sub-step per agent, such as 4.1 to 4.3, each ticked as its
agent reports, in any order; once the last reports, the sub-steps go and the step returns, ticked.
One list shows all progress, and its ticks always match what has really finished. The lifecycle page's[^lifecycle]
"Showing progress" section says how in each place:

| Place | What the agent does |
| --- | --- |
| Claude Code command line and desktop | Fills the live task list Claude Code shows |
| Claude project thread[^thread] | Fills the checklist the app shows |
| With no such list | Prints the steps, then one line as each step or sub-step ends |

## Background

[ADR 0062](0062-show-progress-checklist.md) put long runs' steps on each place's list. A step with
several helper agents, such as a build's three reviews, then showed one running line for many
minutes. A project thread's checklist cannot indent lines and lists finished lines first.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Replace the step by its sub-steps while it runs | Chosen | Each agent shows as it finishes |
| One line per step only | Rejected | A step of several agents sits still for minutes |
| Sub-steps as a tree under the step | Rejected | Finished lines moving first breaks the tree |
| The step kept running above its sub-steps | Rejected | Finished sub-steps are listed above it |
| State in words, emojis or a growing summary | Rejected | A second way of showing progress |
| Replies, a progress bar or a diagram | Rejected | Nothing shows the whole list |

## Consequences

- Good: the person sees which step and agent a run is on.
- Bad: on the command line and desktop, each change of layout takes several updates.
- Bad: the rule relies on how each place shows its list.
- Bad: a long step with no helper agents leaves the list still.

## Out of scope

- How the steps are listed and when the agent is prompted to update them, which [ADR 0063](0063-scripts-list-steps-hook.md) decides.
- Thread work that is not a skill run, and other tools, such as editor extensions.

## How we'll check

Applies to: how long skill runs show their progress.

1. Inspection: the places and sub-step layout appear only in the lifecycle page's "Showing progress" section.
2. Test: the check script fails a skill in Technical detail's table that does not point to that section.
3. Test: a command-line build of a test project shows its reviews as sub-steps, then their step ticked.
4. Demonstration: on desktop and in a project thread, the same build shows the same layout.

## Open questions

None.

## Technical detail

**Telling apart where the agent runs.** The agent goes by the tools it has. A project thread gives it a tool
that posts the thread's checklist: it uses that, since it is what the person sees there. Otherwise
it uses Claude Code's task tools, `TaskCreate` and `TaskUpdate` (`TodoWrite` in older versions).
With none of these, it prints the numbered lines.

**Lines.** Each step is numbered, and a finished line reads "4. Reviews of the code: 2 bugs, 1
failed check" beside the list's mark for done. A sub-step is numbered from its step, as "4.2 Security review", and its finished line
carries its own summary. Lines carry only the list's own marks for done, running and not started, which in a project
thread and in printed lines are ✓, ✱ and ○: no other emojis or words for state. In the
project thread's checklist a step's number is written `4\.`, so the app does not indent the line as
a list and it lines up with `4.1`.

**Sub-steps.** A step splits into sub-steps only when it starts more than one helper agent; a step with one
agent, such as a correction check, stays one line. The sub-steps are made as the step starts, when
its agents are known, and each is ticked as its own agent's report is in, whether the agents run
side by side or one after another. Once every sub-step is ticked, the sub-steps are removed and the
step is put back in their place, ticked, with a summary of them all.

**Keeping the order on the command line and desktop.** `TaskCreate` adds a task to the end of the
list, so a sub-step cannot be put in the middle. When a step splits into sub-steps, the agent deletes that step
and every step after it not yet started (`TaskUpdate`, status `deleted`), then makes the sub-steps,
then makes the deleted later steps again. When the step returns, it deletes the sub-steps and the
later steps, makes the step again and marks it completed, then makes the later steps again. Steps
not yet started hold no state, so nothing is lost. `TodoWrite` and the project thread's tool write
the whole list each time, so there the agent writes the list as it should now stand.

**The skills and their steps.**

| Skill | Shown when | Steps | Steps that split into sub-steps |
| --- | --- | --- | --- |
| /build, which builds code from a plan (the document describing the work) | the checks before building pass | one per requirement of the plan, in the order the plan lists them; reviews of the code; corrections; check that the corrections broke nothing; give the person the work and reports | reviews of the code: build review, security review, code review |
| /audit, which looks for code and documents that disagree | its script has listed the documents to check | check each document; recheck the findings; report | check each document: one per spec[^spec] or ADR, and the brief[^brief] when it is checked; recheck the findings: one per document with findings |
| /verify, which tries the running product against its specs | the person agrees the list | one per spec; report | each spec: try its examples, then try to disprove the verdicts |
| Document review in the commands that write documents: /brief, /spec, /adr, /plan, /practices | the review starts | review; corrections; check that the corrections broke nothing; give the person the document and reports | review: review against the skill's list of pass-or-fail checks; check for words a newcomer could not follow |
| /spike[^spike] | the run starts | one per run of the experiment; review of the experiment's result | none |
| /deploy, which puts a release live | the person says yes | deploy; check, which can wait minutes to pass; reply | none |

A step the run turns out not to need, such as corrections after a review that found nothing, is
marked done with that as its summary. A step that would split into a single agent, such as a recheck
of only one document's findings, stays one line.

**The project-thread list moves.** Each update moves the checklist to the newest point in the
thread, and the app lists finished lines first, then the running one, then those not started, so
sub-steps finished out of order show above those still running.

**Evidence.** In a project thread on 2026-11-26, a checklist was posted, six long messages followed,
and then the checklist was updated: the person saw it leave its first place and appear at the newest
point. On 2026-11-27, demonstrations in a project thread showed that the checklist drops
indentation, lists finished lines first, and indents a line starting `3. ` as a list but not one
starting `4.1`; the person approved the layout above after watching it run.

[^skill]: A skill is a set of instructions the agent follows for one step of the plugin, run as a command such as /build.
[^helper]: A helper agent is a separate agent the skill starts to do one part of the work, such as a review, and that reports back when done.
[^thread]: A Claude project thread is a conversation inside a project on claude.ai, where the agent runs on a remote machine and the person sees only its replies, its checklist and the files it attaches.
[^lifecycle]: The lifecycle page is the plugin's one page of shared rules, which the agent is given at the start of a session in a repository that uses the plugin's way of building software.
[^spike]: A spike is a throwaway experiment that settles one unknown before a decision is made.
[^brief]: A brief is the document that says what the product is, who it is for and why.
[^spec]: A spec is the document that says what one capability of the product should do.
