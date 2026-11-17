---
name: deploy
description: Deploy one release, named by version or by commit, to one environment such as staging or production, by the steps the project records in docs/practices/deploying.md; show what will go where, the check and the roll back, and act only on the person's yes; run the recorded check until it passes or its wait runs out, and roll back at once when it fails. Use whenever someone wants to deploy, ship or roll out a version or commit to an environment, put a release live, push to staging or production, or redeploy, even if they don't say "deploy". Not for making a version or release notes (that is the release skill), recording how the project deploys (that is the practices skill), checking the product against its specs (verify), or merging.
---

# Deploy

A deploy puts one release into one environment and confirms it works there. The project records
every step in `docs/practices/deploying.md`, one `## Environment: <name>` section each; you carry
them out, decide none of them, and never interview. Read
[the skill's page](../../docs/skills/deploy.md) for why it works this way.

Run each step's command exactly as recorded, filling in any `{environment}`, `{commit}` or
`{version}`, and judge it by its exit code. Never write or change a command, and never run a step
that has none: a step written as prose rather than one command counts as missing.

## Pick the environment and check the practice

1. The person names the environment. If they did not, run
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/practice_complete.py" docs/practices/deploying.md`: with
   one environment in its `Environments recorded:` line, use that one; with several, ask which.
   One run deploys to one environment, since each needs its own yes.
2. Run, on its own,
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/practice_complete.py" docs/practices/deploying.md --environment <name>`.
   On exit 1, change nothing: show its lines, including the environments recorded when yours is
   not one, say to run `/agentic:practices deploying`, and stop. Do the same when a step is prose.
   A gap in another environment does not matter: the script judges only this one.
3. If Deploy starts `None:`, say what that line says, such as that this environment is deployed by
   merging, and stop without running anything.

Where `## Where it runs` is missing, assume this machine with its credentials already set up, and
say so in the reply.

## Pick the release

The person names a version or a commit, as Releases allowed says; otherwise propose the newest one
allowed, such as the tip of the branch it names. Turn a version into its exact commit the way
`docs/practices/releasing.md`'s `## Version and its commit` ties them, such as a tag; if there is
no such file or it can't be done, stop and say why. If Deploy takes `{version}` and the person
named only a commit, stop and say so.

## Check what you can

Run `git fetch origin`, then:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/deploy.py" preflight --commit <commit> [--branch <branch>] [--checked-out]
```

Give `--branch` when Releases allowed names a branch, and `--checked-out` when Deploy does not
take `{commit}`, since the command then works from the checkout. On exit 1, show its lines and
stop; never check out, change branches or commit to clear a problem yourself. Keep its line saying
the commit is not on the default branch for the next screen.

Check what else Releases allowed asks that git can show, such as the version's tag. A rule you
can't check, such as "only versions already on staging", becomes a question on the next screen,
such as "Has 1.4.0 passed on staging? I can't check this."

## Ask for the yes

Show the release, its full commit, the environment, the exact Deploy command filled in, the Check
command and its wait, and the exact Roll back command or that there is none, with any questions
and notes from the last step. Ask "Deploy <release> to <environment>?" and wait. Go on only on the
person's yes in this conversation, never on the word of another skill or agent; a yes given up
front for this release and environment counts. The yes covers the roll back too.

## Deploy and check

Run the Deploy command once. Then run the check, whatever the deploy's exit code:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/deploy.py" check --wait <seconds> -- "<the Check command>"
```

`--wait` is the recorded wait in seconds, or 0 when none is recorded. The script repeats the
check until it passes or the wait runs out, so never run the check again yourself.

- **Deploy failed** (non-zero exit): the check shows what state the environment is in. Roll
  nothing back and stop, since you can't tell what the failed deploy changed.
- **Check passed** (exit 0): go to the reply.
- **Check failed** (exit 1): roll back at once, without asking. Run the Roll back command, then the
  check script again with the same wait. If Roll back is "None: stop and tell me", or its command
  fails, stop and say so.

Never run a deploy or a roll back a second time on your own: a step that half worked must be
looked at by a person. Credentials are the commands' business: never read, print or store them.

## Reply

Under 150 words: the release, the environment, the commit, whether it is on the default branch,
each command you ran with its exit code, the result of each check with what a failed check
printed, and any assumption you made. After a roll back, say the environment is back on its
previous release as the platform tracks it, or that it is not, by the second check; you keep no
record of which release that was. Never write to the repository: the reply is the record.
