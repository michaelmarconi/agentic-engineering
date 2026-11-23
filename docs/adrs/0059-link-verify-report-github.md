---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0059
status: Draft 📝
date: 2026-11-23
---

# Link the verify report to the spec on GitHub at the commit checked

## Question

How does the report a verify run[^verify] ends with let a person jump from each requirement and
example[^example] to what the spec says about it?

## Decision

Chosen: when the repository's main remote is on GitHub, each requirement and example in the
report links to its place in the spec on GitHub at the commit checked; otherwise each is shown
as plain text with its line number in the spec, and the report says why there are no links. The
report sits outside the repository, so only a full web address reaches the spec, and pinning it
to the commit keeps it right after the spec changes.

## Background

The report names requirements and examples, but the reader must open the spec and search for each
one. The report file lives in a folder for the session's temporary files, outside the repository, as
[ADR 0051](0051-every-file-outside-scratchpad.md) decided, so a link relative to the repository
does not work from it. Pull request descriptions already use full GitHub links pinned to a commit,
under [ADR 0057](0057-refuse-pull-request-description.md).

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| GitHub links at the commit checked, plain text with line numbers elsewhere | Chosen | Works on GitHub, as pull requests do, and still points the way elsewhere |
| Links relative to the repository | Rejected | The report sits outside the repository, so they do not open |
| Links for every hosting service | Rejected | Each service shapes its web addresses differently, and nobody has asked for another yet |
| No links | Rejected | The reader keeps searching the spec by hand |

## Consequences

- Good: on GitHub, one click opens the spec at the exact requirement or example checked.
- Good: a link still points at what was checked after the spec changes.
- Bad: a repository hosted elsewhere gets line numbers, not links.

## Out of scope

- The report's layout, which [ADR 0058](0058-script-lays-out-verify-report.md) decides.
- A private repository's links, which open only for people allowed to read it.

## How we'll check

Applies to: the links the verify report gives to the spec.

1. Test: unit tests give GitHub remotes in their usual forms and check each link the script builds.
2. Test: unit tests give a remote on another service, and none, and check plain names with line numbers.
3. Inspection: in a trial run on a GitHub repository, each link in the report opens the right place.

## Open questions

None.

## Technical detail

**Remote.** The main remote is the one named `origin`. The script that writes the verify report,
`skills/verify/scripts/verify.py`, reads `git remote get-url origin`. It counts as GitHub when it is
`https://github.com/<owner>/<repo>[.git]`, `git@github.com:<owner>/<repo>[.git]` or
`ssh://git@github.com/<owner>/<repo>[.git]`. Anything else, or no `origin`, gets plain text.

**Links.** The base is `https://github.com/<owner>/<repo>/blob/<7-character commit>/<spec path>`,
the short commit keeping links under the 150 characters
[ADR 0057](0057-refuse-pull-request-description.md) found GitHub turns into plain text.

- The spec, in the header: the base.
- A requirement: the base, then `#` and the anchor GitHub gives its heading: lowercase, punctuation other than hyphens and underscores dropped, spaces made
  hyphens, so `### 2. Reply to all` gives `#2-reply-to-all`.
- An example: the base, then `?plain=1#L<line>`, the line of the example's table row in the spec
  at that commit, since a table row has no anchor.

**Plain text.** A requirement or an example reads `<name> (line <n>)`, and the header adds:
"Links to the spec were left out because the repository's `origin` is not on GitHub."

**Lines.** The script reads the spec as it is at the commit checked, with `git show
<commit>:<path>`, so line numbers and anchors match the linked version.

[^verify]: A verify run is the plugin's step that starts the product and uses it from outside, as a person would, to check it against its specs.
[^example]: In a spec, a requirement is one numbered rule the product must follow, and an example is one case under it, a row of a table with a starting state, an action and the expected result, that can be tried on the product.
