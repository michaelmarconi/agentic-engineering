---
name: verify
description: Check the running product against its accepted specs from the outside. Agree with the person which requirements to check, then one fresh agent per spec starts the product as the Running the product practice says, tries each example the way a person would and gives it pass, fail or not checked with evidence, never reading the code, and a second agent tries to disprove each verdict. Ends with a report file and a short reply, and changes nothing in the repository. Use after a build and before merging, or whenever someone wants to know whether the product actually does what its specs say, to try it out, demo it against the spec or sanity check a feature end to end, even if they don't say "verify". Not for checking the code against the specs or ADRs without running it (an audit), for running the test suite, or for writing lasting tests.
---

# Verify

A verify run checks the product against its `Accepted 👍` specs from the outside: agents start the
product, use it through its real interfaces, and give each example of the agreed requirements a
verdict with evidence. They never read the code, so they can only judge what the product does.
The run changes nothing in the repository and sets no status, so the person decides what follows.
Before you start, read [references/rubric.md](references/rubric.md) with the Read tool: it is the
list of checks the run must meet.

The verify script does the exact checks. Run it with Bash, from the repository's root, or with
`--project <folder>` when the repository is not the folder you are in:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/verify.py" <command> ...
```

- `start [<spec path> ...] --scratchpad "<your scratchpad folder>" --session "${CLAUDE_SESSION_ID}"` refuses
  while anything is uncommitted, since the report must name the version it checked; otherwise it
  prints the commit, and each spec named, or every spec when none is, with its status and its
  requirements, each with how many examples it holds. Run it first in every run, before any agent.
- `report` writes the report file, as Report says.

Give as `--scratchpad` the scratchpad folder your instructions name, exactly as they write it, so the file is somewhere the person's app can open; leave the option out only when they name none.

If a command exits with 1, or Claude Code doesn't let it run, stop and give the person its reason:
check nothing. Never work its checks out yourself instead.

## What to check

Every run checks a list of requirements, each from an accepted spec, agreed with the person first.
Read what they asked for:

- requirements by name or number, such as "requirements 2 and 7 of the mail pull spec";
- one or more whole specs, or every accepted spec;
- a plan, which stands for the requirements its Specs section names. Read only that section: the
  rest of a plan is about the code.

When they named nothing, propose the requirements of the plan this branch marked `Built ✅`, the
one whose status the branch's own commits changed, if there is one; otherwise ask what to check.

Run `start` with the specs those requirements come from, or with none for every spec. Then show
the person the list you will check: each spec by its path, with its requirements by number and
name and how many examples each holds, as `start` printed them. Leave out every requirement whose
spec is not `Accepted 👍`, and say so with its status: a spec that is not accepted states no
settled intent to check against. Leave out, too, a spec `start` marks `old_layout`, whose
requirements it cannot list, and say it must be brought to the current layout with `/spec` and
accepted again. Tell them the second agent re-challenges every verdict, passes included, so
each spec takes about twice as long as one agent alone, and that the requirements a change
touches are usually enough. Ask the person to confirm or change the list, and check nothing
until they agree. When their request already named what to check and said to go ahead, that is
their agreement: show the list and carry on. If they change the list, run `start` again with its
specs.

## Running the product

The agents start and use the product as the project's Running the product practice says, so read
it before any agent starts: the `## Practices` section of `AGENTS.md` and of `CLAUDE.md`, whichever
have one, and the file under `docs/practices/` it names for running the product.

- **None recorded.** Start no agent. Say that verifying needs it, and ask the person to record it
  with `/agentic:practices running the product`, commit it, and run `/agentic:verify` again.
- **Another machine.** When it names a machine or operating system this session is not running
  on, which `uname -s` shows, start no agent and say why.

Never write or change the practice yourself: what is safe to touch is the person's call.

## Check each spec

Check the specs one after another, never side by side, since each agent starts and stops the
product. For each spec in the agreed list, start the `agentic:verifier` agent in the foreground,
with this request:

```
Document: <the spec's full path>
Repository: <root, as start printed it>
Requirements:
<number>. <name>
...
```

Name only the agreed requirements of that spec. Give the agent nothing else, not the code, a plan,
another document or anything from this conversation: it must judge only by what the product does.

When it has reported, start the `agentic:verify-checker` agent in the foreground, with the
verifier's report copied between the markers exactly as it came, since the person judges each
verdict by its evidence:

```
Document: <the spec's full path>
Repository: <root, as start printed it>
=== VERIFIER REPORT ===
<the report>
=== END VERIFIER REPORT ===
```

A report with an `Error:` line checked nothing: start no checker for it, and report that spec's
requirements as not checked, never as passed. When the verifier says the product did not start,
the practice no longer works: check no further spec, and ask the person to correct it with
`/agentic:practices running the product`.

Judge each verdict by the checker's word on it. A confirmed verdict stands. A rejected one is
**disputed**: report it with both agents' evidence and the verdict each reached, for the person to
decide. Never settle a dispute yourself, and never read the code or tests to judge one.

## Report

However the run ends once `start` has passed, end with a report file; a run stopped by the script
writes none, and its reply gives the reason. The script copies every agent's report into it word
for word and fills the commit checked; you write only your own sections, as Markdown under these
`##` headings, in this order, each grouped by spec under a `### <spec path>` line, leaving out any
you have nothing for:

1. `## Overall result`: every example passed, or how many failed, are disputed or were not checked.
2. `## Failed`: each confirmed fail, by requirement and example, with the evidence and its
   suggested next step: **correct the code**, through `/plan` and `/build` or directly when small;
   or **return the spec to `Draft 📝`** and change it, through `/spec`, when the product is right
   and the spec is not.
3. `## Disputed`: each rejected verdict, with both agents' evidence.
4. `## Not checked`: each example not checked, with its reason and what would make it checkable,
   such as a way to set the product's clock; and every requirement of a spec whose agent reported an
   `Error:`, or that the run stopped before, with why. If the run stopped, say why here.
5. `## Passed`: each confirmed pass, by requirement and example.

Give your sections to the script on standard input, with `--commit` set to the commit `start`
printed and `--scope` set to a few words naming what was checked, such as the spec's name:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/verify.py" report --scope "<scope>" --commit <commit> --scratchpad "<your scratchpad folder>" --session "${CLAUDE_SESSION_ID}" <<'EOF'
## Overall result

...
EOF
```

It prints the file's path first, then the file as written. If it refuses a heading, correct your
sections and run it again. Never write or edit the file yourself. Its last section says whether a
file in the repository changed during the run, such as a lock file the product rewrote; mention it
in the reply if one did.

End with a short reply, under 150 words: the outcome in a sentence or two, then at most five
bullets of at most 15 words each, with the main findings and any question or action for the
person, then the report file's full path; if the app you run in can show them a file in a viewer,
show the report file there; never paste the report or its sections into the reply, since the file
holds them.

Make no correction. The run writes, edits and deletes nothing in the repository, sets no status
and makes no commit, so the person chooses what follows: merge, correct the code, or change the
spec. If they then ask for one, that is a new request.
