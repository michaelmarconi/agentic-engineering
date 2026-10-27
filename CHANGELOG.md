# Changelog

What changed in each version of the plugin, newest first. Versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html), and this file follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Read the entry before you update
past a major version: it says what you need to change in your documents. Until 1.0.0, any
minor version may need such a change, and its entry says so.

## [0.5.0] - 2026-10-27

### Added

- `/adr` records one technical decision as an ADR (architecture decision record) in
  `docs/adrs/NNNN-<title>.md`, using the core of the MADR format: the context, the options
  considered and why each lost, the decision, its good and bad consequences, and a Confirmation
  saying what it applies to and how to check the code follows it. It drafts from your
  conversation, writes one ADR per decision, and has each one reviewed before you see it.
- ADRs move from Draft to Accepted or Rejected, and from Accepted to Superseded when a newer ADR
  replaces them. Only you can accept or reject an ADR: `/adr` asks you once the reviewed text is
  final.
- The status hook now covers ADRs too: it refuses status changes the lifecycle does not allow,
  and any edit to an ADR that is no longer a Draft, apart from marking it Superseded by an
  accepted replacement.

### Changed

- ADRs live in `docs/adrs/`, not `docs/decisions/`, and start as Draft rather than Proposed.

## [0.4.1] - 2026-10-27

### Added

- This changelog. Claude Code tells you when the plugin has updated but not what changed, so
  each version now has an entry here; the README's Update section points to it.

### Changed

- The plugin's versions follow Semantic Versioning: a fix is a patch, a new skill or new
  behaviour is a minor version, and a change that breaks documents you already have, or the
  lifecycle, is a major version. Until 1.0.0, a breaking change bumps the minor version and
  its entry says what breaks.

## [0.4.0] - 2026-10-27

### Added

- `/brief` writes or changes your product brief, `docs/brief.md`: the one short document that
  says what the product is, who it is for, why it exists and how you will know it works. It
  has a one-line summary and sections for Problem, Who it's for, Goals, Out of scope,
  Constraints and Open questions. Unlike a spec, a brief has no status.
- `/brief` drafts from what you have already said, reads only what you point it to, and asks
  before reading anything else. It gives the number of open questions and asks them one at a
  time, and it explains every acronym the first time it appears, title included.
- A brief reviewer checks the draft against the brief rubric before you see it. Where the
  brief links a document in your repo, the reviewer also checks the brief against it. Any
  remaining decisions are left to you.

## [0.3.0] - 2026-10-27

### Added

- `/issue` reports a bug or suggests an improvement in this plugin. It drafts the issue from
  the plugin's bug or improvement template, filling in Context with the plugin, Claude Code and
  operating system versions, and it can propose an eval case for the fix.
- Your project's details stay out of the issue: `/issue` paraphrases rather than quoting your
  repo, and replaces real names and code with stand-ins. An issue reviewer checks the draft
  before you see it.
- Nothing is filed until you approve the draft. `/issue` then files it with `gh`, as the
  GitHub account it showed you, or gives you a pre-filled link to submit yourself.

## [0.2.1] - 2026-10-27

### Added

- `/spec` writes or changes a spec with you: one living document per capability under
  `docs/specs/`, with sections for Problem, Goal, Scope, Requirements, Constraints and Open
  questions. Each requirement is one rule with Given/When/Then scenarios and a "Verified by:"
  line saying how it will be checked.
- `/spec` drafts from what you have already said and asks only about the gaps: it gives the
  number of open questions, then asks them one at a time. It keeps technical choices out of
  the spec and adds no behaviour you didn't ask for.
- A spec reviewer, which always runs on Sonnet, checks every draft against the spec rubric
  before you see it. It separates decisions only you can make, which block Ready to build,
  from suggestions, which don't. `/spec` fixes what it can and passes the rest to you.
- Spec statuses: Draft, Ready to build and Built. A spec becomes Ready to build only once you
  have seen its final text, it has no open questions and its review has passed. Built is
  reserved for `/build`, which isn't released yet.
- A session-start hook that gives Claude a short map of the lifecycle, only in repos that use
  it.
- A hook that refuses spec edits making a status change the lifecycle doesn't allow, such as
  skipping Draft or setting Ready to build while open questions remain.

## [0.1.1] - 2026-10-26

### Changed

- The README now explains the whole lifecycle for a reader starting with no context: the
  Planning steps (`/brief`, `/spec`, `/spike`, `/adr`, `/plan`), Building (`/build`) and
  `/audit`. Each skill has its own page under `docs/skills/`; for skills not yet released,
  that page is a placeholder.

## [0.1.0] - 2026-10-22

### Added

- The plugin and its own marketplace, so you can install it with
  `claude plugin marketplace add michaelmarconi/sdlc` and `claude plugin install sdlc@sdlc`.
  It has no skills yet.
