---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0055
status: Draft 📝
date: 2026-11-22
supersedes: 0025
---

# Show each file the way each of the three places needs, written once on the lifecycle page

## Question

When a skill[^skill] hands the person a file it wrote, such as a document to review or a report,
how does it show that file so the person can open it?

## Decision

Chosen: one section of the lifecycle page[^lifecycle], "Showing a file to you", says what to do in
each of the three places the plugin runs, and every skill points to it with one line, because the
places differ too much for one general sentence. The three places:

| Place | What the agent does |
| --- | --- |
| Claude Code command line | Names the file's full path |
| Claude Code desktop | Opens the file in the Files pane and names its full path |
| Claude project thread[^thread] | Copies the file into the project's shared files folder, attaches the copy to its reply and names the copy's path, again after each change |

In every place, the agent never sends the person to a code-hosting site.

## Background

[ADR 0025](0025-document-review-display.md) gave every document skill one general sentence: show
the file in the app's viewer if it has one, and always name its full path. In a Claude project
thread the agent works on a cloud machine the person never sees, so that path leads nowhere,
and the person cannot read the document they are asked to review. Reports share the problem. [ADR 0053](0053-review-sequence-lifecycle-page.md)
already moved the review steps to the lifecycle page, so each skill points there.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| One general sentence: a viewer or an attached copy, naming a path the person can open | Rejected | General wording has already failed in project threads |
| Add a project-thread line to the sentence in every skill | Rejected | Repeats the same special cases in nine skills |
| Name the three places once, on the lifecycle page, with a pointer line in each skill | Chosen | Each place is handled exactly, in one copy |

## Consequences

- Good: the person can open every document and report in each of the three places.
- Good: a change to one place, or a fourth place, means editing one section.
- Bad: the project-thread case names that app's shared folder, so it must change if the app does.
- Bad: a skill must read another file at its hand-over, and might skim it.

## Out of scope

- Places other than the three, such as the editor extensions.
- Where reports are written, which [ADR 0051](0051-every-file-outside-scratchpad.md) settles: the project-thread copy only shows a report.

## How we'll check

Applies to: how every skill shows the person a file it wrote or changed.

1. Inspection: the three places appear only in the lifecycle page's section, in no skill.
2. Test: the check script fails a skill that shows a file without the pointer line.
3. Test: the check script fails a lifecycle page whose section lacks one of the three places.
4. Demonstration: in a project thread, the reply giving the person a new spec attaches a copy from the shared files folder.

## Open questions

None.

## Technical detail

**Telling the places apart.** A project thread's own instructions name the shared files folder,
`/mnt/project-files/`, and give the agent a tool that posts replies with attached files. Claude
Code desktop gives the agent a way to open a file in its Files pane. Without either, the agent is on
the command line.

**The section.** "Showing a file to you" sits on the lifecycle page beside the Review process
section, and holds the three places and the code-hosting rule as the Decision states them.

**Which skills.** The reply that gives the person the finished document in /brief, /spec, /adr,
/plan, /spike and /practices, and the closing reply of /build, /verify and /audit. Each holds one
pointer line, worded the same, in place of the two sentences on showing a document and a report
that `scripts/skill_check.py` checks today. The script checks
the pointer line in each, checks that the section holds each place, and fails a skill that copies
the old sentences back. Each skill keeps what is its own, such as giving the reports and the number
of questions.

**The test cases.** The plugin's recorded test cases, which run a skill and grade its output, gain
a project-thread case. It gives the agent a test folder at `/mnt/project-files/` and instructions
naming it, and checks that a copy of the spec exists there and the reply names that
copy's path.

[^skill]: A skill is a set of instructions the agent follows for one step of the plugin, run as a command such as /spec.
[^thread]: A Claude project thread is a conversation inside a project on claude.ai, where the agent runs on a remote machine and the person sees only its replies and the files it attaches. The project's shared files folder is the one folder there the person can open.
[^lifecycle]: The lifecycle page is the plugin's one page of shared rules, which the agent is given at the start of a session in a repository that uses the lifecycle.
