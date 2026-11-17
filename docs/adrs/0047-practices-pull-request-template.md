---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-17
---

# The practices skill offers a pull request template

## Question

How does the plugin help a project's pull requests read well and follow the same sections every time?

## Decision

Chosen: when a project's practices[^practices] say it uses pull requests on GitHub, the practices
skill[^skill] offers a pull request template from a default the plugin ships. It writes the template
only on yes, leaves an existing one alone, and asks whether the project is on GitHub when it cannot
tell. The reviews and merging practice then gains a rule that descriptions follow the template, so
agents opening pull requests through tools use it too. When there is no template, because the
project is not on GitHub or the person declines one, the same sections are recorded as that
practice's rule instead. This is chosen because GitHub shows the template to everyone opening a pull
request on its web page, with nothing new to run.

## Background

Pull request descriptions without set sections open with detail, hiding what they are for and
which plan[^plan], specs[^spec] and ADRs[^adr] they carry out. The plugin changes nothing in a project
beyond the practices the person chooses. [ADR 0042](0042-practices-skill-writes-commands.md) and
[ADR 0045](0045-practices-skill-writes-scripts.md) let the practices skill write command runner
entries and scripts; this ADR adds a pull request template.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| A new skill that writes pull request descriptions | Rejected | Covers only pull requests opened through it |
| A reviewer that checks each description against a list of checks | Rejected | More to set up and run |
| A practice that lists the sections, with no template | Rejected | People writing on GitHub's web page never see it |
| The practices skill offers a template from a shipped default | Chosen | Authors see it where they write |

## Consequences

- Good: every pull request opened from the template starts from the same sections.
- Good: a reviewer sees which plan, specs and ADRs a pull request carries out.
- Bad: the practices skill writes one more file outside the practices themselves.
- Bad: a template only suggests sections; nothing stops an author deleting them.

## Out of scope

- The template's sections and wording: content of the shipped default, changed without a new ADR.
- Opening, reviewing or merging pull requests: the plugin still does none of these.

## How we'll check

Applies to: the practices skill's topic on reviews and merging.

1. Test: on GitHub, the skill offers the template and writes it only on yes.
2. Test: an existing template is left as it is.
3. Test: off GitHub, the sections go in the reviews and merging practice, with no template.
4. Test: when the person declines the template, the sections go in that practice instead.
5. Inspection: the default opens with a plain summary, then what the work carries out.

## Open questions

- None.

## Technical detail

**Where it is offered.** In the Reviews and merging topic, once the person says the project uses
pull requests. The project is on GitHub when its `origin` remote names `github.com` or it already
has a `.github/` folder; otherwise the skill asks.

**What it writes.** `.github/pull_request_template.md`, copied from the default in the practices
skill's `assets/`, shown to the person before it is written. Any existing template, at that path,
at the root, in `docs/`, or in a `.github/PULL_REQUEST_TEMPLATE/` folder, is left alone and noted
in the practice. Either way, the reviews and merging practice gains one rule: pull request
descriptions follow the template, naming its path.

**The default's sections**, in order: Summary, two to four plain sentences on the problem, what
changes for the people who use the product and what the reviewer should look at; Built from, a link
to the plan the work followed, then the specs and requirements it delivers and the ADRs it follows,
laid out as the plan lays them out, or "No plan"; What changes; How it was checked; Notes, optional, for choices, defects fixed and
anything left to check. Each section's guidance names the section of the report that
`/agentic:build` writes when it finishes, from which that content is taken.

**No template.** Not on GitHub, or when the person declines one, the skill records the same sections as a rule in the reviews and merging
practice: its `merging.md` topic file when there is one, otherwise the Practices section.

[^skill]: A skill is a set of instructions Claude follows for one step, started as a slash command such as `/agentic:practices`.
[^practices]: Practices are the project's recorded ways of doing things, one topic at a time, in a short section of `AGENTS.md` and files under `docs/practices/`.
[^plan]: A plan is the lifecycle's document for one piece of work: it names the specs and ADRs the work delivers and says how it will be done.
[^spec]: A spec says what one capability of the product should do, as numbered requirements.
[^adr]: An ADR records one technical decision and why it was made.
