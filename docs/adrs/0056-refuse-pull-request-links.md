---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0056
status: Superseded ↪️
date: 2026-11-22
superseded-by: 0057
---

# Refuse a pull request description whose links would break

## Question

How does the plugin keep the links an agent writes in a pull request description working?

## Decision

Chosen: a hook[^hook] refuses to create or edit a pull request whose description holds a link
longer than 150 characters, and says how to shorten each one: pin it to the 7-character commit id,
or, if still too long, link the file without its heading anchor. Running every time, it catches the link before it reaches GitHub.

## Background

[ADR 0047](0047-practices-pull-request-template.md) gives projects a pull request template whose
Built from section links the plan, specs and architecture decision records (ADRs) the work came
from, each at the commit being proposed. Agents follow it with full 40-character commit ids, and a
link to one requirement adds the requirement's heading to the address. In pull requests opened that way, exactly the links over
150 characters were saved wrapped in code formatting, so they showed as text rather than as links.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Tell agents in the template to use the short commit id | Rejected | Left to the agent, and missing where a project has its own template or none |
| Have the agent read the description back after opening the pull request and fix it | Rejected | The broken description is already published, and the agent must remember |
| Refuse a description with a link that would break, before it is sent | Chosen | Runs every time, before anything reaches GitHub, in every repository with the plugin |

## Consequences

- Good: every link in a pull request description the agent writes is short enough to work.
- Good: the check comes with the plugin, changing nothing in the repository.
- Bad: an attempt with a long link is refused and must be made again.
- Bad: a link that would work at 151 characters is refused, since the limit comes from what was
  seen, not a documented rule.

## Out of scope

- Why long links were saved as code, which the plugin cannot change.
- Pull requests made other than by the GitHub tool or the `gh` command.
- Comments, reviews and issues, and hosts other than GitHub.
- The template's wording, which [ADR 0047](0047-practices-pull-request-template.md) leaves open.
- Pull requests opened before the hook existed.
- A request the hook cannot read, such as an unreadable description file, which passes.

## How we'll check

Applies to: any pull request an agent creates or edits while the plugin is installed.

1. Test: unit tests give the hook requests with links of 150 characters and fewer, and with a
   link over 150 characters; only the first pass.
2. Test: unit tests check that every other tool call, and every other shell command, passes.
3. Demonstration: in a trial repository, an agent opening a pull request with long links is
   refused, shortens them and tries again.

## Open questions

- None.

## Technical detail

**The hook.** `scripts/pr_link_check.py` runs just before each tool call whose name matches
`Bash|mcp__.*__(create|update)_pull_request`. It reads the description:

- for the GitHub tool, the `body` argument;
- for a shell command that runs `gh pr create` or `gh pr edit`, the whole command's text, which
  holds the `--body` value or a here-document, plus the contents of any `--body-file` or `-F`
  file it can read.

Every other command and tool call passes untouched.

**What is refused.** Each link address, both a Markdown link's target and a bare `http` or `https`
address, is measured in characters, its heading anchor included. The request is refused when one
is longer than 150 characters. A short link pinned to a full 40-character commit id passes.

**The refusal's reason.** It lists each link with its length, and says to pin file links to the
7-character commit id, which GitHub accepts in the same place. If a link is still too long, it
says to link the file without the heading anchor and name the heading in the text.

**Evidence.** In one pull request opened this way, the three links of 152, 163 and 170 characters
were saved wrapped in backticks inside the link, and every link of 148 characters or fewer worked.
With the 7-character id, the longest of those links is 137 characters.

[^hook]: A hook is a script the coding tool runs automatically at set moments, here just before the agent sends a pull request to GitHub.
