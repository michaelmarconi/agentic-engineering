# Releasing

## What may be released

Only `main`, and only code already merged there.

## Version and its commit

Semantic versioning. The version lives in `VERSION`. A release is the commit that changes `VERSION`
to the new version; there are no tags.

## Publish

`make publish VERSION={version}`

## Release notes

A Keep a Changelog entry at the top of `CHANGELOG.md`, headed `## [X.Y.Z] - YYYY-MM-DD`, with
`### Added` and `### Fixed` sections as needed.

## When to release

Batched: when enough is merged, on a short-lived branch `release/<version>` cut from `main`, which
a person merges.
