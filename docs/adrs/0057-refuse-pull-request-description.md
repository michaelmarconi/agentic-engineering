---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0057
status: Draft 📝
date: 2026-11-22
supersedes: 0056
---

# Refuse a pull request description unless it is written out with short links

## Question

How does the plugin keep the links in an agent's pull request description working, whether it is
sent through the GitHub tool or a shell command?

## Decision

Chosen: a hook[^hook] refuses to create or edit a pull request when its description is not written
out, because a file it names cannot be read or a link is still to be completed by the shell, or
when it holds a link longer than 150 characters. Only a written-out description can be checked,
and checking every time stops long links reaching GitHub. The refusal says what to change, such as
writing the description out first or pinning a long link to the 7-character commit id.

## Background

[ADR 0056](0056-refuse-pull-request-links.md) refuses a description holding a link over 150
characters, since GitHub was seen saving such links as code rather than as links. That hook lets
through a description it cannot read. In a shell command, an agent can build the description and
send it at once, before the hook can read it. In a trial, the long links got through that way.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Keep letting through a description the hook cannot read | Rejected | Sending it in a shell command, as agents often do, then skips the check |
| Work out what the shell would produce before it runs | Rejected | Needs the hook to act as a shell, and still misses cases |
| Refuse a description that is not written out before it is sent | Chosen | The hook then sees the finished text whichever way it is sent |

## Consequences

- Good: every link the agent sends in a pull request description is short enough to work.
- Good: the check comes with the plugin, changing nothing in the repository.
- Bad: an attempt with a long link, or with a description not yet written out, is refused and
  must be made again.
- Bad: a working link of 151 characters is refused too, as the limit was seen, not documented.

## Out of scope

- Why long links were saved as code, which the plugin cannot change.
- Pull requests made other than by the agent's GitHub pull request tool or the `gh` command.
- Comments, reviews and issues, and hosts other than GitHub.
- The wording of the pull request template, which [ADR 0047](0047-practices-pull-request-template.md) leaves open.
- Pull requests opened before the hook existed.

## How we'll check

Applies to: any pull request an agent creates or edits while the plugin is installed.

1. Test: unit tests give the hook requests with short links and a link over 150 characters; only
   the first pass.
2. Test: unit tests give the hook a `gh` request whose description file does not exist yet, and
   one whose link is built by the shell; both are refused.
3. Test: unit tests check that every other tool call and shell command passes.
4. Demonstration: a sample conversation opening a pull request with long links sends every link at
   150 characters or fewer.

## Open questions

- None.

## Technical detail

**The hook.** `scripts/pr_link_check.py` runs just before each tool call whose name matches
`Bash|mcp__.*__(create|update)_pull_request`. It reads the description:

- for the GitHub tool, the `body` argument, which is always written out;
- for each `gh pr create` or `gh pr edit` a shell command runs, on any line and after any variable
  settings: that command's own words, any here-document on its line, and the file named by
  `--body-file` or `-F`, found from the event's working folder and any `cd` before it.

Every other command and tool call passes untouched.

**Not written out.** A `gh` request is refused as not written out when a body file it names cannot
be read, or when a link address in its description holds a shell variable or command, such as
`$B/docs/…` or `$(git rev-parse HEAD)`. A body read from standard input is checked through the
here-document that feeds it. A `$` elsewhere in the text, such as "costs $5", is left alone. The
reason says to write the description file in one command and run `gh` in the next, or to pass the
description inline with every link written out.

**Too long.** Each link address, both a Markdown link's target and a bare `http` or `https` address,
is measured in characters, its heading anchor included. The request is refused when one is longer
than 150 characters. The reason lists each such link with its length and says to pin file links to
the 7-character commit id, which GitHub accepts in the same place; if a link is still too long, to
link the file without its heading anchor and name the heading in the text.

**Evidence.** In one pull request opened through the GitHub tool, the three links of 152, 163 and
170 characters were saved wrapped in backticks inside the link, and every link of 148 characters or
fewer worked. With the 7-character id, the longest of those links is 137 characters. In a trial of
[ADR 0056](0056-refuse-pull-request-links.md)'s hook, the agent set a shell variable to a link's
start, wrote the description to a new file with links such as `$B/docs/specs/…`, and sent that file
with `gh pr create --body-file`, all in one command; the hook found no file to read and let it
through.

[^hook]: A hook is a script the coding tool runs automatically at set moments, here just before the agent sends a pull request to GitHub.
