---
status: 👍 Accepted
date: 2026-10-28
---

# Number versions as major.minor.patch, and describe every release in a change log

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. Claude Code
updates a person's installed copy only when the version written in the plugin's manifest, its
description file, changes. It does not tell the person what the new version changed. Some
changes need the person to act, such as a change to the lifecycle that their existing documents
must follow.

So each release needs a version people can read, which says how much changed, and somewhere that
says what changed and what, if anything, they must do. This records a decision made on
2026-10-27.

## Considered Options

- **No version in the manifest**, so that Claude Code tracks the code by its commit identifier,
  the unique code git gives each saved change. Rejected: the identifier says nothing to a person,
  who cannot tell a small fix from a change that breaks their documents.
- **Versions named by release date.** Rejected: a date says when a release happened, not whether
  it breaks anything.
- **Semantic versions without a change log.** Rejected: the number would say that something
  breaks, but not what it is or what to do about it.
- **Semantic versions, explained by a change log.** A semantic version has three numbers,
  major.minor.patch: the patch number rises for a fix, the minor number for new behaviour, and
  the major number for a change that breaks documents people already have. A change log is a
  file listing what each version changed, newest first. Chosen, below.

## Decision Outcome

Chosen option: semantic versions, explained by a change log, because the number tells people at a
glance whether an update can break anything, and the change log tells them what changed and what
to do.

### Consequences

- Good: people can see from the number alone whether an update needs their attention.
- Good: the change log is written for the people who use the plugin, so it explains changes in
  their terms.
- Bad: the maintainer must judge the size of every change, and a wrong judgement misleads
  people.
- Bad: a change merged without a new version never reaches people who already have the plugin.

### Confirmation

Applies to: every release of the plugin.
Checked by: test. A script, run in the change that sets a new version, checks that the newest
change log entry names the manifest's version and is newer than the entry below it.
