---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-10
supersedes: 0023
---

# Refuse links to outside material with a hook that checks every edit to the five kinds of document

## Question

How does the plugin stop each of its five kinds of document from referring to outside material?

## Decision

Chosen: a hook[^hook] that checks each edit Claude makes to the five kinds of document, refusing
any new link to outside material. A script applies the rule exactly, and one
rule for every kind stays simple.

## Background

This plugin for Claude Code, Anthropic's AI coding assistant, has skills[^skill] writing five kinds
of document: the brief[^brief], specs[^spec], ADRs[^adr], plans[^plan] and spike records[^spike].
Each must make sense without outside material, such as notes it was drafted from, and may refer
to such material only by a web link. [ADR 0023](0023-outside-material-references.md) enforced
this by a hook for the first three kinds, leaving the rest to reviewer agents[^reviewer].

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Keep the hook to the brief, specs and ADRs | Rejected | The same rule would be enforced two ways, depending on the document |
| Leave every document to the reviewer agents | Rejected | A reviewer agent reading a long document can miss a link that a script never misses |
| The hook checks all five kinds of document | Chosen | One rule, applied the same way to all five |

## Consequences

- Good: Claude cannot add a link to outside material to any of the five kinds, whether or not a
  skill is running.
- Good: the refusal names each link, so Claude restates the material in its own words at once.
- Bad: a plan or spike record Claude writes with such a link is refused and has to be written again.

## Out of scope

- A mention of material by name, or a path written as plain text. Neither is a link, so the
  reviewer agents catch them.
- Links to other paths in the repository, such as code, which pass.
- Edits not made with Claude's file-editing tools.
- Links a document already held before the edit, which stay until someone removes them.
- Which kinds may refer to which, left to the reviewer agents.

## How we'll check

Applies to: any edit Claude makes to one of the five kinds of document.

1. Test: unit tests give the hook edits to each of the five kinds and check what it allows and refuses.
2. Test: for each skill that writes a document, a sample conversation hands over notes, and the document written refers to them in no way.

## Open questions

- None.

## Technical detail

**The hook.** `scripts/reference_check.py` runs just before each Write, Edit or MultiEdit. It is
started by the same script as the hook of [ADR 0005](0005-status-change-hook.md), which refuses a
change to a document's status that the plugin's rules do not allow, and runs after that check. It
checks the project's brief and every file in its spec, ADR, plan and spike record folders. It works out the file as the edit would leave it and reads every
link, image, reference definition, autolink and HTML `href` or `src` outside code spans and fenced
code blocks.

**What it refuses.** An edit is refused if it adds a target that:

- is an address of a kind other than `http`, `https` or `mailto`, such as `file:`;
- starts at the root of the computer or at a home folder (`~`);
- leads outside the repository;
- is a file under `docs/` that is not one of the five kinds of document.

Any other target passes, such as a heading in the same document or a folder.

**Spike records.** A spike record names its inputs as values in backticks, and its code sits in
fenced blocks, so neither is read as a link.

[^hook]: A hook is a script Claude Code runs automatically at set moments, here just before Claude edits a file.
[^skill]: A skill is a set of instructions Claude follows for one step, run as a slash command.
[^brief]: The brief is the one document that says what the product is and who it is for.
[^adr]: An ADR (architecture decision record) is the write-up of one technical decision and why it was made.
[^spec]: A spec says what one capability of the product should do.
[^plan]: A plan sets out one piece of work that builds part of a spec or an ADR.
[^spike]: A spike record is the write-up of one throwaway experiment that settles an unknown.
[^reviewer]: A reviewer agent is a separate Claude that checks each document against a list of checks.
