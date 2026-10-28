# Review relay: hooks versus pasting

Run 2026-10-27/28. Question: after a review, can the correction checker be given the review report
and the document as reviewed exactly, without writing files into the person's repository?

**Answer: yes, by hooks, and pasting is close but not exact.** A hook carried both texts exactly
in 30 of 30 runs. A Sonnet drafting agent pasting them itself changed a word in 2 of 30 runs; an
Opus drafting agent pasted exactly in 30 of 30.

## How the hook works

`plugin/` is a throwaway plugin. Its hook (`plugin/scripts/relay.py`) uses only documented hook
fields:

- Before the reviewer starts (`PreToolUse` on `Agent`), it saves the document named on the
  request's first line, `Document: <path>`. The reviewer cannot edit, so this is the text as
  reviewed.
- When the reviewer finishes (`PostToolUse` on `Agent`), it saves the report from
  `tool_response.content`, or from `SubagentHandback`'s `tool_input.message` when the reviewer
  hands back that way.
- Before the correction checker starts (`PreToolUse` on `Agent`), it appends both, between fixed
  markers, to the checker's request through `updatedInput`. It refuses to start the checker when
  no review is on record, or when the document is unchanged since its review.
- Everything is saved under `$CLAUDE_PLUGIN_DATA` (`~/.claude/plugins/data/<plugin>/`), outside
  the project, and deleted when the checker finishes. No permission prompt appeared.

## Setup

- Corpus: the 10 specs from `../review-seeding/corpus` (8 with planted defects, 2 clean).
- Each run: `claude -p` with the plugin, a drafting agent given `drafter-hook.md` or
  `drafter-paste.md` (review, read the spec, correct once, start the checker), 3 runs per spec.
- Arms: inject (Sonnet drafting agent, hook carries the texts), paste (Sonnet drafting agent
  copies them), paste-opus (Opus drafting agent copies them). Reviewer and checker on Sonnet.
- `score.py` compares, line by line, what reached the checker with the reviewer's actual reply
  and the file as it was reviewed.

## Results

| Measure | inject | paste (Sonnet) | paste (Opus) |
|---|---|---|---|
| Report reached the checker exactly | 30/30 | 29/30 | 30/30 |
| Reviewed text reached the checker exactly | 30/30 | 29/30 | 30/30 |
| Runs with any copying change | 0/30 | 2/30 | 0/30 |
| Correction check passed | 14/30 | 12/30 | 15/30 |
| Cost per run (relative) | $0.19 | $0.22 | $0.36 |

Sonnet's two changes, each a single line, both silent:

- A review finding: "the two-hour **cancellation** cut-off" became "the two-hour cut-off".
- The reviewed spec: "removes the middle member" became "removing the middle member".

Neither changed the meaning here. Both show the copy is a rewrite, not a copy: on a longer report
or a harder finding the same habit could drop or soften something, and nothing would notice.

## A separate finding: corrections break things

Only about half of all runs passed the correction check, against 26 of 30 for arm D of the
seeding experiment. Of the 49 failed checks, 49 found a correction that broke something, and only
3 found a correction not made. The difference from arm D is the correcting instructions: arm D's
`fixer.md` gave the rubric and said "leave suggestions alone, make no other changes"; this
experiment's drafting prompt did neither. So the correct step needs the rubric in front of it and
a narrow brief, which the real skills must give it.

## Limits

- 30 runs per arm. Sonnet's 2/30 is a rate of roughly 1 in 15, with wide uncertainty.
- Reports here were 2 to 4 KB and specs 40 to 110 lines. Longer texts give more chance to slip.
- The drafting agent was a short scripted prompt, not the real `/spec` skill mid-conversation,
  where the report sits further back in a longer context.

## Reproduce

```
python3 run.py --out results/<name> --modes inject,paste,paste-opus --runs 3 --jobs 8
python3 score.py --out results/<name>
```
