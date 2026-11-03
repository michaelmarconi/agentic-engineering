---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 👍 Accepted
date: 2026-10-30
---

# Spec status describes the document, not the software

## Context and Problem Statement

This repository is a plugin, an add-on, for Claude Code, Anthropic's AI coding assistant. The
plugin helps a person write a software project's documents, such as architecture decision
records (ADRs) like this one. Another is a specification, or spec: the intended behaviour of one
capability of the product, written as requirements, each with example scenarios and a line saying
how to check it. A third is a plan: a signed-off description of one piece of work that builds
part of a spec. Each spec carries a status, and a status could describe either the document,
such as whether its intent is settled, or the software, such as whether it meets every
requirement.

The software keeps changing after it is built: later work, small corrections made without a plan,
tests that are removed. A spec can also be built in parts by several pieces of work, and some
requirements can only be checked by a person running the software. A status that records the
state of the software is true only at the moment it is set, and nothing notices when it stops
being true. So we need to decide what a spec's status describes.

## Considered Options

- **A `✅ Built` status, set when the work is built and checked.** Rejected: it goes stale the
  first time the software changes without the spec, and a spec built in parts, or with
  requirements only a person can check, never fits one status.
- **A record of "built" and "checked by a person" for every requirement, with the spec's status
  worked out from them.** Rejected: each record goes stale in the same way, only at a finer
  level, and a hook cannot tell whether a person really did the check it records.
- **Merge each finished change into the specs, as [OpenSpec](https://openspec.dev/docs/getting-started)
  does.** OpenSpec keeps specs that "describe how your system currently behaves". When a change
  is archived, its added, changed and removed requirements are merged into those specs, after an
  optional check of that one change that its own instructions call advisory. Rejected: merging
  records that a change was made, not that the system still behaves that way. Nothing checks the
  specs against the code afterwards, so they gradually stop matching the code as it changes, and
  are no guarantee of what the system ends up doing.
- **A spec's status describes only the document: `📝 Draft` or `👍 Accepted`.** A person accepts
  a spec once its intent is settled, as they accept an ADR, and any later edit returns it to
  `📝 Draft`. The name no longer ties the spec to building, which is a plan's concern. Whether the
  software meets the spec is answered when someone needs to know, by checking the software
  against the spec at that time.

## Decision Outcome

Chosen option: a spec's status describes only the document, because it never claims anything it
cannot keep true. The spec stays the statement of what the software should do, and the software
is measured against it whenever the answer matters.

### Consequences

- Good: no status can become false without anyone noticing, however the code changes.
- Good: specs built in parts, and requirements only a person can check, need no special status.
- Good: a spec's status works like an ADR's, which describes the decision, not the code, and
  uses the same word for a person's sign-off.
- Bad: a spec no longer shows whether it has been built. Finding out means checking the software
  against it, or reading the plans used to build it.
- Bad: the plugin's description of the steps its documents go through, the status-change hook
  (ADR 0005) and the rule for when a plan may be built all change to match.

### Confirmation

Applies to: the statuses a spec can have.
Checked by: test. The status-change hook's tests show it refuses any spec status other than
`📝 Draft` and `👍 Accepted`.

## Open questions

- None.
