---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-10-28
---

# Plan without Claude Code's plan mode

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. The
plugin helps a person write a software project's documents. One of them is a plan: a short-lived
document that says how one piece of work will build part of what the project's specifications and
architecture decision records (ADRs) have settled. The person signs a plan off, and it is kept
until the work is built, possibly later and by someone else.

Claude Code has its own plan mode. In it, Claude explores the code without changing anything,
writes a plan, and asks the person to approve it before editing anything. The plugin's planning
skill has to decide whether to run inside plan mode or to plan by itself.

Every skill in the plugin is tested with `claude plugin eval`, Claude Code's own test command
(ADR 0006), which runs it on sample conversations in non-interactive sessions, and must pass on
every supported model before it is released (ADR 0008).

## Considered Options

- **Run the skill inside plan mode.** The skill enters plan mode, writes the plan there, has it
  reviewed, and saves it to the project once the person approves. Rejected: in a throwaway
  experiment with Claude Code 2.1.312, this worked in three of three interactive terminal runs,
  but in non-interactive sessions the tools that enter and leave plan mode do not exist, and the
  plugin's test runner has no setting to start in plan mode. So the skill's main path could not be
  tested. Plan mode's approval is also an approval to start coding: its approval prompt asks
  "Ready to code?", while a plan here is signed off and kept for later.
- **Plan by itself, following the same steps as plan mode.** The skill explores first, using Claude
  Code's built-in Explore and Plan helper agents, which change nothing, then settles each technical
  decision with the person, then writes the plan for the person to sign off. Not plan mode but two
  parts of the plugin guard the sign-off: a Claude Code hook that refuses a change to a document's
  status that breaks the plugin's rules (ADR 0005), and a separate agent that reviews each document
  once, with its corrections checked afterwards (ADR 0010).

## Decision Outcome

Chosen option: plan by itself, following the same steps as plan mode, because it runs and can be
tested wherever the plugin runs. In a separate check with the same version, non-interactive
sessions on two Claude models, Sonnet and Opus, each started the Explore and Plan helper agents
and got their answers back.

### Consequences

- Good: the skill behaves the same in every session, and its tests cover the path people use.
- Good: signing off a plan is a step of the plugin's own process for writing documents, with no
  wording about starting to code.
- Bad: the skill does not get improvements Anthropic makes to plan mode; we must notice them and
  make the same changes to the skill where they help.
- Bad: people who know plan mode may expect `/plan` to start it, and in the terminal a bare
  `/plan` does start plan mode.

### Confirmation

Applies to: how the plugin's planning skill explores and asks for sign-off.
Checked by: inspection. The skill's instructions never enter or leave plan mode, and its tests
run in non-interactive sessions.

## Open questions

- None.
