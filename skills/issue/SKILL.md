---
name: issue
description: Report a bug or suggest an improvement in the sdlc plugin itself (its skills, agents, hooks or lifecycle) by drafting a redacted GitHub issue on the plugin's own repository, with enough context for a maintainer to reproduce it. Use whenever someone says an sdlc skill such as /spec got something wrong, the lifecycle got in their way, or they want to give the plugin's maintainers feedback, even if they don't say "issue". Not for issues about the person's own project.
---

# Issue

An issue is how the plugin learns. A maintainer reads it with none of this conversation and
none of the person's repository, turns it into a failing eval case, and fixes the plugin until
the case passes. So the issue must stand on its own, and because the plugin's repository is
public, it must carry nothing from the person's repository.

Before drafting, read [references/rubric.md](references/rubric.md): it is the list of checks
the reviewer will apply, so drafting to it saves rounds.

## Gather

Take what the conversation already shows: which skill, agent or hook was involved, what it was
asked, and what it did. Ask the person only for what is still missing, one question at a time:
what happened, what they expected instead, and whether it happens every time. If the problem
turns out to be in their own project rather than in the plugin, say so and stop.

Decide the kind: a **bug** when the plugin did something wrong, an **improvement** when it
worked as designed but could work better. Read that kind's template,
`${CLAUDE_PLUGIN_ROOT}/.github/ISSUE_TEMPLATE/bug.md` or `improvement.md`, and keep its headings,
as Markdown headings, in order.

For the versions in Context, run:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/issue.py" context
```

If you can't run it, read the plugin's version from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`
and give the other versions as unknown.

## Draft

Write the title and body in the template's shape, as rubric checks 1 to 8 describe. Redact as
you write rather than after: describe the person's project only in general terms, rebuild any
example from stand-ins, and quote nothing from their repository, not even a line that looks
harmless. A maintainer needs the shape of the problem, not the person's content. If the person
asks to keep something you would redact, keep it and say why it is a risk: it is their
information, so the reviewer's report and the decision are theirs, not yours.

Keep the draft in the conversation. Never write it to a file in the person's repository: the
plugin leaves nothing there but the lifecycle's own documents.

## Review

The draft is reviewed up to ${user_config.review_rounds} times, counting the first. If no number
appears in that sentence, the plugin's Review rounds setting has not been saved: run no review.
Show the person the draft, say it is unreviewed and can't be filed yet, and ask them to run
`/plugin configure sdlc@sdlc`, type a number next to Review rounds, choose Save configuration,
run `/reload-plugins` and then ask you for the review. Never pick a number yourself.

Otherwise, start the `sdlc:issue-reviewer` agent in the foreground, not in the background, and give it the
kind and the draft, title and body, in full and word for word. It reads everything else it needs
itself. Wait for its report before changing the draft, so the report matches the draft. It
reports pass or fail for each rubric check with evidence, other findings, and anything that
needs the person.

Fix every finding you can and run the reviewer again, until the limit. If the last review still
fails, show the person the draft and the report, say what is still failing, and ask how they
want it changed; each change they make gets one more review. A failing draft is filed only if
the person, with the report in front of them, says to file it anyway: it is their information to
share.

## File

Run `python3 "${CLAUDE_SKILL_DIR}/scripts/issue.py" account` to learn how it would be filed:
`gh <login>` means with the GitHub CLI as that account, `link` means they submit it in their
browser. Show the person the draft exactly as it would be filed, the reviewer's final report,
and, for `gh <login>`, that it will appear under that account, since their name is public on the
issue and it may be a work account. Then ask whether to file it.

File only on their clear yes to that draft: an issue on a public repository can't be taken back,
so a yes given before they have seen the draft and the account doesn't count, even "file it, I
trust you" in their first message. This holds for a link too: run `file` only after the yes,
since a link is one click from public. If they change
the draft, review it again before asking again. If they bring back a draft and say yes to it,
review it and run `account`. If the review fails, handle it as under Review. If it passes and
`account` says `link`, or they asked for a link, give them the link without asking again,
since they submit it themselves; if it says `gh <login>`, tell them the account and ask once
more.

On their yes, pass the draft on standard input: the bare title alone on the first line, with no
heading mark or "Title:", then the body. The quoted delimiter keeps the shell from expanding
anything in the draft. Use `--as <login>` with the account they agreed to, or `--link-only` for
a link:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/issue.py" file --kind <bug|improvement> --as <login> <<'SDLC_ISSUE_DRAFT'
<title>

<body>
SDLC_ISSUE_DRAFT
```

It prints `filed <issue URL>`, or with `--link-only`, `link <URL>`: give the person that link,
which opens the issue already filled in for them to submit. Any other exit code comes with a
message saying why; tell the person, and:

- 2: the first line wasn't a bare title, or there was no body; fix the command and rerun it.
- 6: the CLI is now signed in as a different account; nothing was filed. Ask the person again.
- 3: the draft is too long. Offer a shorter draft, which is reviewed again.
- 4: the CLI ran but failed, and may have filed it anyway. Give the person the CLI's message and
  the repository's issues page it names. Only once they have checked that the issue isn't there,
  run the same command again, or use `--link-only` if the CLI keeps failing.
- 5: nothing was filed: the CLI couldn't confirm its account or GitHub refused the issue.
  Offer the link instead, which they submit under whichever account their browser uses.
- 1: the plugin's own files are missing or broken, so there is nowhere to file.
