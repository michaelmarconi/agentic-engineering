# Changelog

What changed in each version of the plugin, newest first. Versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html), and this file follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Read the entry before you update
past a major version: it says what you need to change in your documents. Until 1.0.0, any
minor version may need such a change, and its entry says so.

## [0.9.0] - 2026-10-29

### Changed

- Every document status now starts with an emoji: `📝 Draft`, `🟢 Ready to build`, `✅ Built`,
  `👍 Accepted`, `❌ Rejected` and `↪️ Superseded`. New specs and ADRs are written that way, and
  the plugin's pages name each status the same way.
- The plugin's hook now refuses a status written without its emoji, or with the wrong one, and
  says what to write instead. **This affects documents you already have.** A spec or ADR whose
  status is a bare word, such as `status: Accepted`, still counts as that status, but the next
  change Claude makes to it must also add the emoji. A change that only adds the emoji to the
  status line is always allowed, even on an ADR that is already decided. To bring every document
  over at once, ask Claude to add the emoji to each status line under `docs/specs/` and
  `docs/adrs/`.

## [0.8.0] - 2026-10-29

### Added

- A language checker reads every document `/spec`, `/brief`, `/adr` and `/issue` write, at the
  same time as the skill's reviewer, and reports any words someone new to your project could not
  follow. The skill corrects what both reports find in its one round of corrections, and the
  correction checker checks those corrections too. The reasons, with the measurements behind
  them, are in this plugin's ADR 0013.
- A Plain words rule in the lifecycle page says what the checker holds documents to: computing
  terms are used freely, a term from your product's own field gets a footnote defining it where
  it first appears, and anything else a newcomer would not know, such as a team nickname or a
  figure of speech, is rewritten in plain words.

### Changed

- The brief's rubric no longer has its own plain words check, since the language checker now
  does that job for every skill.
- The note at the top of a new spec or ADR, and the prompt in the spec template's Problem
  section, are reworded in plain words.
- When a new spec conflicts with another spec, the hand-over names that spec and the rule that
  conflicts, since the spec itself cannot refer to it.

## [0.7.0] - 2026-10-28

### Changed

- `/spec`, `/brief`, `/adr` and `/issue` now take every document through a fixed review
  sequence: one review, one round of corrections, then a check of only those corrections by a
  shared correction checker. If the check fails, the skill stops and shows you its report rather
  than reviewing again. The reasons, with the measurements behind them, are in this plugin's
  ADRs 0010 and 0011.
- When the sequence ends, the skill gives you the review report, the check's report, the number
  of items left for you to settle, and then asks you about the first of them only. The reviewers'
  suggestions are listed separately as optional.
- `/adr` is also used when you ask to review or correct an existing ADR.

### Added

- A hook hands the correction checker the review report and the document as it was reviewed,
  word for word. It keeps them in the plugin's own data folder, outside your repository, and
  deletes them when the check is done or the session ends.
- A hook lets the plugin's skills and agents read the plugin's own files, such as a rubric,
  without asking you each time. It approves reads inside the plugin's folder only.

## [0.6.0] - 2026-10-27

### Added

- A new rule for the whole lifecycle: documents refer to one another only where neither end can
  go stale. A plan refers to the specs and ADRs it builds, and an ADR to the ADR it supersedes or
  that supersedes it. The brief, specs and ADRs never refer to one another in any way, whether
  by hyperlink, path or title, because either end can change or be deleted without the other
  being touched. The README and the summary Claude gets at the start of each session say so.
- The spec and brief rubrics have a References check, so their reviewers flag any such
  reference. When you ask `/spec` or `/brief` to add one, it leaves it out and tells you why.
  The brief still links to source material, such as a survey, as before.

### Changed

- A spec or brief you already have that refers to another lifecycle document now fails review
  the next time `/spec` or `/brief` changes it, which removes the reference. Nothing else in
  your documents needs to change.

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
