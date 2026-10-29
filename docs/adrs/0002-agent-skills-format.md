---
status: Accepted
date: 2026-10-28
---

# Write skills in the Agent Skills format

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. Its skills are
folders of instructions that Claude follows, one per step of the work, such as writing a spec.
Each skill needs a file layout that Claude Code can load, that lets Claude choose the skill from
a short description, and that keeps longer material, such as a list of review checks or a
template, out of Claude's way until it is needed.

Skills also tend to grow. In an earlier plugin by the same author, skills outgrew a 500-line
budget and mixed step-by-step instructions with policy and notes about past incidents, which
made them hard to follow and change. The format should come with limits that keep a skill small.
This records a decision made on 2026-10-22, when the repository was set up.

## Considered Options

- **Claude Code slash commands**, one Markdown file per command. Rejected: a command is a single
  file, so a skill's checks, templates and scripts would have to live elsewhere.
- **A format of our own.** Rejected: Claude Code would not load it, and Anthropic's
  skill-creator, a skill for writing and testing skills, would not work on it.
- **The Agent Skills specification**, an open standard for skills published at
  agentskills.io. Chosen, below.

## Decision Outcome

Chosen option: the Agent Skills specification, because Claude Code loads skills in this format
and picks one from its description, a skill can keep its extra files beside it and read them only
when needed, skill-creator builds and tests skills in it, and the specification sets limits that keep
skills small. It limits a skill's name to 64 characters and its description to 1,024, and
recommends keeping its main file under 500 lines; we treat that recommendation as a hard limit.

### Consequences

- Good: Claude Code and skill-creator work on our skills as they are.
- Good: the specification's limits, with its recommended length treated as a hard limit, give a
  ceiling on how large a skill may grow.
- Bad: we follow a specification we do not control, and must change our skills if it changes.
- Bad: Claude Code's own plugin validator does not check the specification's limits, so we keep
  a script of our own that does.

### Confirmation

Applies to: every skill in the plugin.
Checked by: test. A script checks every skill's name, description and length against the
specification's limits, and the plugin's script tests run it on the whole plugin, so they fail
when any skill breaks a limit.
