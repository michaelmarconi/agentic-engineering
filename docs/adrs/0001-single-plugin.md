---
status: Accepted
date: 2026-10-28
---

# Ship the skills together as one installable package

## Context and Problem Statement

This repository holds a set of skills for Claude Code, Anthropic's AI coding assistant, that
together take software work from an idea to code on the main branch. A skill is a folder of
instructions that Claude follows for one step, such as writing a spec, the document that says
what one feature must do. The skills also share other parts: reviewer agents (separate instances
of Claude that check a document), hooks (scripts Claude Code runs automatically at set moments)
and helper scripts.

People need to install these in any repository they work in, and to receive later versions. Every
skill depends on at least one shared part, so whatever is installed must bring those parts too.
Claude Code can install a plugin, its unit for packaging skills, agents and hooks together, from a
marketplace, a repository that lists plugins people can install.
This records a decision made on 2026-10-22, when the repository was set up, and confirmed on
2026-10-26.

## Considered Options

- **Each skill installed on its own**, copied into a project's or a person's skills folder.
  Rejected: a lone skill cannot bring the agents, hooks and scripts it shares with the others,
  copying into a project writes into it, and a copied skill has no version to update from.
- **A plugin published from a separate marketplace repository.** Rejected: a second repository to keep in step, for one product
  with one maintainer.
- **One plugin, with this repository as its own marketplace.** Chosen, below.

## Decision Outcome

Chosen option: one plugin, with this repository as its own marketplace, because a single install
brings every skill with the parts they share, and updates arrive by the plugin's version.

### Consequences

- Good: one pair of commands installs everything, and later versions arrive through Claude
  Code's own update mechanism.
- Good: skills can share agents, hooks and scripts instead of each carrying its own copy.
- Bad: a person cannot take one skill without the rest.
- Bad: installing copies the whole repository into Claude Code's plugin folder on the person's
  computer, including this repository's own documents and tests. Claude Code uses only the
  skills, agents and hooks from it, and the scripts they run.

### Confirmation

Applies to: how the plugin is packaged, published and installed.
Checked by: demonstration. Adding this repository as a marketplace and installing the plugin
from it, in a clean Claude Code configuration, makes every skill available, and Claude Code's
plugin validator reports no problem with the manifests.
