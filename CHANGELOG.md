# Changelog

What changed in each version of the plugin, newest first. Versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html), and this file follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Read the entry before you update
past a major version: it says what you need to change in your documents. Until 1.0.0, any
minor version may need such a change, and its entry says so.

## [0.3.0] - 2026-10-27

### Added

- `/issue` reports a bug or suggests an improvement in this plugin, with your project's details
  left out, and files it on GitHub once you approve the draft.

## [0.2.1] - 2026-10-27

### Added

- `/spec` writes or changes a spec with you and has it reviewed before you see it.
- The `review_rounds` setting: how many reviews a skill may run before it stops to ask you.
- A session-start map of the lifecycle, shown only in repos that use it, with a reminder when
  a setting isn't saved.
- A check that blocks spec status changes the lifecycle doesn't allow.

## [0.1.1] - 2026-10-26

### Changed

- The README describes the lifecycle, with a page per skill.

## [0.1.0] - 2026-10-22

### Added

- The plugin and its marketplace, with no skills yet.
