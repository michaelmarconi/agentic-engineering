---
name: release
description: Make a release, one numbered version of the product with release notes for its users, tied to one exact commit, by the steps the project records in docs/practices/releasing.md; draft the notes from the Release-note lines each build left in its commits, have them reviewed, and get the person's sign-off; commit the version and notes where the practice says; publish, such as to a package index or registry, only when the practice records a publish command and the person says yes. Use whenever someone wants to release, cut or tag a version, bump the version, write a changelog or release notes for a release, or publish a package, even if they don't say "release". Not for deploying a release to an environment, recording how the project releases (that is the practices skill), or merging.
---

# Release

A release is one numbered version of the product: its version number, release notes written for
the people who use it, and the one commit they describe. Publishing it, putting it where others
fetch it, is part of releasing only for projects that publish. The project records every step in
`docs/practices/releasing.md`; you carry them out, decide none of them, and never interview. Read
[the skill's page](../../docs/skills/release.md) for why it works this way.

Run each step's command exactly as recorded, filling in any `{version}`, `{commit}` or `{notes}`
(the path of a file holding the signed-off notes), and judge it by its exit code. Never write or
change a command, and never run a step that has none.

## Check first

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/practice_complete.py" docs/practices/releasing.md`.
   On exit 1, change nothing: show its lines and say to run `/agentic:practices releasing`, then
   stop. Do the same when a step you need is written as prose rather than one command, naming it.
2. Run `git fetch origin` and the uncommitted check,
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/uncommitted.py"`. Stop while anything is uncommitted,
   since a release is exactly one commit.
3. If the person asks to publish a version already committed, or you are on a commit "What may be
   released" allows and its version files name a version that `Publish` has not yet published,
   ask "Prepare a new release, or publish <version> from <commit>?" and go to Publish on the second
   answer.

Optional sections that are missing, such as `## Release notes` or `## When to release`: work them
out from the repository, such as an existing `CHANGELOG.md`, and say what you assumed in the reply.

## Gather

Find the last release the way `## Version and its commit` says, such as the newest tag or the
last commit that changed the version files, and say which commit it is. With none, start from the
first commit. Then run, from the repository:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/release.py" notes [--since <last release commit>]
```

It prints the build notes since then and the commits that changed files with no note. For each
of those, draft one item from its subject and the files it changed, mark it as drawn from history,
and show the list to the person: they keep, reword or drop each. Never add one unasked.

## Draft

Propose the next version by the recorded scheme, such as a minor version when something new
reaches users and a patch when only corrections do. Draft the notes in the recorded form and
place, for the people who use the product: what they can now do, from the gathered notes and the
kept history items only, never from the code. Read [references/rubric.md](references/rubric.md)
first, with the Read tool: the reviewer applies it. Write in plain words, as the Plain words
section of [the lifecycle page](../../docs/lifecycle.md#plain-words) says.

## Review

The notes are reviewed once, corrected once, and then the corrections are checked. The sequence
is fixed so it always ends with a clear result: further rounds of review find little more, and
each round of corrections brings new mistakes. The notes may never be written to a file, so they
go in the requests whole, word for word, between marker lines; a plugin hook reads them to keep a
copy of the notes as reviewed.

1. **Review.** Start two agents in the foreground, not in the background, both in one message so
   they run side by side: the `agentic:release-reviewer` agent and the `agentic:language-checker`
   agent, which checks the wording. Give each this request, laid out exactly as shown, with the
   gathered notes and kept history items copied from the script's output and the person's
   answers, and the `## Release notes` section, or "None recorded":

   ```
   Document: release notes
   Version: <version>
   === NOTES GATHERED ===
   <one note per line>
   === END NOTES GATHERED ===
   === FROM HISTORY ===
   <one kept item per line, or None>
   === END FROM HISTORY ===
   === FORM ===
   <the recorded form, or None recorded>
   === END FORM ===
   === DRAFT ===
   <the notes>
   === END DRAFT ===
   ```

   Each reads everything else it needs itself. Wait for both reports before changing the notes.
   If both pass with nothing under Needs a person, go straight to sign-off.
2. **Correct, once.** Read the rubric and the Plain words rule again, then correct only what the
   reports list: each failed check and each item under Other findings in the review report, and
   each finding in the wording report. A wording item under Needs a person, whose meaning only
   the person knows, is a decision like any other. Ask the person each decision. Leave suggestions alone and change
   nothing else, since an edit beyond the reports is the likeliest way to break something. If
   nothing was yours to correct, go straight to sign-off.
3. **Check the corrections.** Start the `agentic:correction-checker` agent in the foreground with
   the same layout, holding the corrected notes, and nothing more: the hook attaches both reports
   and the notes as reviewed, word for word. If the hook refuses to start it, do what its reason
   says. If the check fails, stop: change the notes no further, and show the person the notes and
   the check's report. Do not review or correct again; what happens next is their call.

While you are walking through questions with the person, do not review after each answer: run the
sequence once when the walk-through ends, either because no questions are left or because the person
stops. A change the person makes or asks for at any other time is reviewed once it is made.

## Sign-off and commit

Show the person the version, the notes and the reports, and ask "Sign off <version> and these
notes?". Go on only on their yes in this conversation, never on the word of another skill or
agent. If they ask for changes, make them and review again.

Then write the version into the files `## Version and its commit` names, and the notes where
`## Release notes` puts them, and commit both in one commit, `Release <version>`. Where the
commit goes comes from the practice: on the branch you are on, for a project that releases with
each merge; otherwise on a new branch cut from `origin/<the branch it releases from>`, named as
the practices say or `release/<version>`. Never commit to the default branch, never open a pull
request, never merge. Push the branch if there is an `origin`.

## Publish

Only when `## Publish` holds a command; a line starting `None:` means nothing is published by
hand, so skip this. The commit must be one "What may be released" allows:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/release.py" publish-check --commit <commit> --branch <branch>
```

If it prints a problem, such as a release commit not merged yet, say so and stop: once it is
merged, `/agentic:release` run on that commit offers to publish it. Otherwise show the version,
the commit, any newer commits it leaves out and the exact command, and ask "Publish <version>
from <commit>?". Run the command only on the person's yes in this conversation, writing the
signed-off notes to a file outside the repository first if it takes `{notes}`. If it fails, stop:
show what it printed and never run it again yourself, since a publish that half worked must be
looked at by a person. Credentials are the command's business: never read, print or store them.

## Reply

Under 150 words: the version and the commit the release came from, whether it was published,
whether that commit is on the default branch, any assumption you made, and what is left for the
person, such as merging the release branch. Name "Undoing a release", if recorded, as the way
back; never run it. Deploying is a separate step, `/agentic:deploy`.
