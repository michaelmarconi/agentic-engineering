---
name: feedback
description: Report a bug or suggest an improvement in the sdlc plugin itself (its skills, agents, hooks or lifecycle) by drafting a redacted GitHub issue on the plugin's own repository, with enough context for a maintainer to reproduce it. Use whenever someone says an sdlc skill such as /spec got something wrong, the lifecycle got in their way, or they want to give the plugin's maintainers feedback, even if they don't say "feedback". Not for issues about the person's own project, or feedback about Claude Code itself.
---

# Feedback

An issue is how the plugin learns. A maintainer reads it with none of this conversation and
none of the person's repository, turns it into a failing eval case, and fixes the plugin until
the case passes. So the issue must stand on its own, and because the plugin's repository is
public, it must carry nothing from the person's repository.

Before drafting, read [references/rubric.md](references/rubric.md): it is the list of checks
the reviewer will apply, so drafting to it leaves less to correct. Write in plain words, as
the Plain words section of [the lifecycle page](../../docs/lifecycle.md#plain-words) says: a
language checker holds every draft to it.

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
python3 "${CLAUDE_SKILL_DIR}/scripts/feedback.py" context
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
plugin leaves nothing there but the lifecycle's own documents and the practices the person asks
it to record.

## Review

The draft is reviewed once, corrected once, and then the corrections are checked. The sequence
is fixed so it always ends with a clear result: further rounds of review find little more, and
each round of corrections brings new mistakes. Because the draft is never saved as a file, it
goes in the requests whole, title and body, word for word, between marker lines; a plugin hook
reads them to keep a copy of the draft as reviewed, outside the person's repository.

1. **Review.** Start two agents in the foreground, not in the background, both in one message
   so they run side by side: the `sdlc:feedback-reviewer` agent and the `sdlc:language-checker`
   agent, which checks the wording. Give each this request, laid out exactly as shown:

   ```
   Document: feedback draft
   Kind: <bug or improvement>
   === DRAFT ===
   <title>

   <body>
   === END DRAFT ===
   ```

   Each reads everything else it needs itself. Wait for both reports before changing the draft.
   If both pass with nothing under Needs a person, go straight to showing the person.
2. **Correct, once.** Read the rubric and the Plain words rule again, then correct only what
   the reports list: each failed check and each item under Other findings in the review report,
   and each finding in the wording report. A wording item under Needs a person, whose
   meaning only the person knows, is a decision like any other. Whether a detail is safe to share is the
   person's decision, so a finding under Needs a person goes to them as a question, never a
   guess. Leave suggestions alone and change nothing else, since an edit beyond the reports is
   the likeliest way to break something. If nothing in the reports was yours to correct, there
   is nothing to check: go straight to showing the person.
3. **Check the corrections.** Start the `sdlc:correction-checker` agent in the foreground with
   the same layout, holding the corrected draft, and nothing more: the hook attaches both reports
   and the draft as reviewed, word for word.

   ```
   Document: feedback draft
   Kind: <bug or improvement>
   === DRAFT ===
   <corrected title>

   <corrected body>
   === END DRAFT ===
   ```

   If the hook refuses to start it, do what its reason says. If the check fails, stop: change
   the draft no further, and show the person the draft and the check's report. Do not review or
   correct again; what happens next is their call.

While you are walking through questions with the person, write each answer in without reviewing. Run
the sequence again once, when the walk-through ends, either because no questions are left or because
the person stops. A change the person asks for at any other time is reviewed once it is made. A
draft whose review or check failed is filed only if the person, with the reports in front of them,
says to file it anyway: it is their information to share.

## File

Run `python3 "${CLAUDE_SKILL_DIR}/scripts/feedback.py" account` to learn how it would be filed:
`gh <login>` means with the GitHub CLI as that account, `link` means they submit it in their browser.
Whether the check passed or failed, end here. Show the person the draft exactly as it would be
filed, the review and wording reports and the check's report, if there was one, and, for `gh <login>`, that it
will appear under that account, since their name is public on the issue and it may be a work
account. Leave out the decisions the reports list for the person: say how many items must be settled
before filing, those decisions plus any correction the check found not made or broken, say you will
take them one at a time, rather than asking whether to, and ask the first only, as a single
question, giving any examples as possible answers rather than further questions; if the person has
said not to ask now, ask nothing. Name the count only, not the items: each comes up when you reach
it. List the reviewers' suggestions separately, as optional. Once nothing is left to settle, ask
whether to file it.

File only on their clear yes to that draft: an issue on a public repository can't be taken back,
so a yes given before they have seen the draft and the account doesn't count, even "file it, I
trust you" in their first message. This holds for a link too: run `file` only after the yes,
since a link is one click from public. If they change
the draft, run the review sequence again before asking again. If they bring back a draft and say yes to it,
run the review sequence on it and run `account`. If the review or check fails, handle it as
under Review. If it passes and
`account` says `link`, or they asked for a link, give them the link without asking again,
since they submit it themselves; if it says `gh <login>`, tell them the account and ask once
more.

On their yes, pass the draft on standard input: the bare title alone on the first line, with no
heading mark or "Title:", then the body. The quoted delimiter keeps the shell from expanding
anything in the draft. Use `--as <login>` with the account they agreed to, or `--link-only` for
a link:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/feedback.py" file --kind <bug|improvement> --as <login> <<'SDLC_FEEDBACK_DRAFT'
<title>

<body>
SDLC_FEEDBACK_DRAFT
```

It prints `filed <issue URL>`, or with `--link-only`, `link <URL>`: give the person that link,
which opens the issue already filled in for them to submit. Any other exit code comes with a
message saying why; tell the person, and:

- 2: the first line wasn't a bare title, or there was no body; fix the command and rerun it.
- 6: the CLI is now signed in as a different account; nothing was filed. Ask the person again.
- 3: the draft is too long. Offer a shorter draft, which goes through the review sequence again.
- 4: the CLI ran but failed, and may have filed it anyway. Give the person the CLI's message and
  the repository's issues page it names. Only once they have checked that the issue isn't there,
  run the same command again, or use `--link-only` if the CLI keeps failing.
- 5: nothing was filed: the CLI couldn't confirm its account or GitHub refused the issue.
  Offer the link instead, which they submit under whichever account their browser uses.
- 1: the plugin's own files are missing or broken, so there is nowhere to file.
