---
type: ADR
status: 👍 Accepted
date: 2026-10-28
---

# Explain the lifecycle to Claude at the start of each session, only in repositories that use it

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. It defines a
lifecycle: the documents a software project keeps, such as a brief for the whole product and a
spec for each feature, the steps that write them and the rules they follow. Each step is a
skill, a set of instructions Claude follows when that step runs. The plugin describes the whole
lifecycle on one page, the lifecycle page.

Skills run one at a time, so a skill on its own does not tell Claude how the steps fit together.
Claude needs that picture in any session in a project that uses the lifecycle, even when no skill
runs, so that it does not, for example, write a feature's behaviour into the brief. The plugin
must work when installed in any repository without changing anything there, apart from the
documents its skills write. A document takes part in the lifecycle when it has a lifecycle status:
a status field at its top, set to one of the values the lifecycle allows, such as Draft. This records a decision made on 2026-10-26, when the first skill was
built.

## Considered Options

- **Ask people to add the lifecycle to their project's CLAUDE.md**, a file of instructions Claude
  Code reads at the start of every session. Rejected: it changes their repository, and each copy
  falls behind when the plugin changes.
- **Repeat the lifecycle in every skill.** Rejected: the same text would sit in every skill, and
  Claude would still not have it in a session where no skill runs.
- **A hook gives Claude the lifecycle page in every session, in every repository.** A hook is a script
  that Claude Code runs automatically at set moments, such as the start of a session. Rejected:
  it would cost space in Claude's working memory in every project that does not use the
  lifecycle.
- **A hook gives Claude the lifecycle page at the start of a session, only when the repository has a
  brief or a spec with a lifecycle status.** Chosen, below.

## Decision Outcome

Chosen option: a hook gives Claude the lifecycle page at the start of a session, only when the
repository has a brief or a spec with a lifecycle status, because Claude then always has the
picture where it is needed, nothing is written into the person's repository, and projects that do
not use the lifecycle pay nothing.

### Consequences

- Good: one copy of the lifecycle page, shipped with the plugin, is what every session sees.
- Good: other projects on the same computer are unaffected.
- Bad: a project's first sessions, before it has a brief or a spec, do not get the lifecycle
  page, and neither does a project that keeps only other lifecycle documents, such as ADRs.
- Bad: every change to the lifecycle page changes what Claude is told in every project that uses
  it, so it needs the same care as a change to a skill.

### Confirmation

Applies to: how Claude is told about the lifecycle in a project that uses the plugin.
Checked by: test. Unit tests run the hook on sample projects and check that it gives the
lifecycle page when a brief or a spec with a lifecycle status is present, and nothing otherwise.
