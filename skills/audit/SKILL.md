---
name: audit
description: Find drift, where the code and its lifecycle documents no longer agree. A script checks every spec, ADR, plan and spike record as it stands, and one fresh agent per accepted spec and ADR checks the code against it, with each drift finding checked again before it is reported with a suggested correction. Covers the whole repository, the commits of a window such as "last 7 days" or "since" a commit, or one named document, and changes nothing. Use whenever someone wants to know whether the code still does what the specs say or follows the ADRs, to check for drift or out-of-date documents, or to run a scheduled audit, even if they don't say "audit". Not for reviewing one change or pull request, for security or dependency checks, or for running tests.
---

# Audit

An audit finds drift: places where the code no longer does what a `👍 Accepted` spec says, or no
longer follows a `👍 Accepted` ADR. It reports what it finds and changes nothing in the
repository, so the person chooses each correction. Before you start, read
[references/rubric.md](references/rubric.md) with the Read tool: it is the list of checks the
audit's output must meet.

The audit script does every exact check. Run it with Bash, from the repository's root:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/audit.py" <command> ...
```

- `documents` checks every lifecycle document and lists the accepted specs and ADRs. Run it in
  every audit.
- `window <words>` lists a window's commits and the files they changed, and writes nothing. Run
  it before anything else when the person gives a window.

Each prints JSON. If a command exits with 1, or Claude Code doesn't let it run, as in a routine
whose permissions don't allow it, stop and give the person the reason: without the script you
can't tell which documents to check. Never work its checks out yourself instead.

## What to check

Read what the person asked for:

- nothing more than an audit: every accepted spec and ADR;
- `last N days` or `since <commit>`: a window, read on the checked-out branch;
- a document's path: that one spec or ADR.

For a window, run `window` first. If it refuses, stop with its reason: check nothing, not even
the documents, and never fall back to a full audit. Then run `documents` in every case. For a
named document, if it is not among `documents`' accepted specs and ADRs, stop and say why: it
doesn't exist, or it isn't `👍 Accepted` and so states no settled intent. Report nothing else.

Say so plainly and go straight to the findings when there is nothing for agents to check: when
`lifecycle` is false there are no lifecycle documents at all, and nothing more to report; when
no spec or ADR is accepted, or a window holds no commits, the document checks are still the
findings.

For a window, start the `sdlc:audit-picker` agent with this request, filled from `window`'s
output and listing every accepted spec and ADR under `Documents:`, one per line:

```
Commits:
<commit> <date> <subject>
...
Changed:
<status> <path>, or R <path> from <old path>
...
Documents:
<path>
...
```

The documents to check are those it picks, and every one `window` lists under
`changed_accepted_documents`, whose own text changed. If that leaves none, say the window's
changes touch no accepted document.

## Check the code

Start one `sdlc:auditor` agent per document to check, all in the foreground and all in one
message, so they run side by side. Give each this request, exactly as shown:

```
Document: <the document's path, as documents lists it>
```

Never start one for any other document. Claude Code limits how many agents run at once; if it
refuses some, start those again the same way once the others have reported, until every
document has a report.

Then, for each report whose Drift section is not "None.", start one `sdlc:audit-checker` agent,
all in one message, with this request. Copy the auditor's report between the markers exactly as
it came, since the person judges each finding by its quotes:

```
Document: <the document's path>
=== AUDIT REPORT ===
<the report>
=== END AUDIT REPORT ===
```

A drift finding is reported as drift only once its checker confirms it.

## Report

Give the findings in this order, grouped by document within each part, leaving out a part with
nothing in it:

1. **Drift:** each confirmed finding, with the auditor's quotes of the requirement or decision
   and of the code, with its file and line, as the report gave them.
2. **Problems with the documents:** each problem `documents` reported, with its document.
3. **Not built yet:** for each spec, how many requirements were not found, and their names.
4. **ADR checks that need a run:** each, with what to run.
5. **Documents to consider deleting:** the `✅ Built` plans and finished spike records. Nothing
   refers to either, so deleting one leaves no other document wrong.
6. **Unfinished spike records:** each `📝 Draft` or `🟢 Ready to run` one, with its date.
7. **Rejected findings:** each, briefly, with the checker's reason.

Name a suggested correction, and the skill that makes it, for each drift finding and each problem:

- **Correct the code**, when the document is right: through `/plan` and `/build`, or directly for
  a small correction;
- **Return the spec to `📝 Draft`** and change it, through `/spec`, when the code is right;
- **Supersede the ADR**, through `/adr`, when the decision no longer holds;
- for a problem with a document, the edit that corrects it.

Make none of them. The audit writes, edits and deletes nothing in the repository, sets no status
and makes no commit, so the person chooses every correction. If they then ask for one, such as
deleting a plan it listed, that is a new request.

Once you have reported, look in the project's practices, in `AGENTS.md`, `CLAUDE.md` and any files
under `docs/practices/`, for what to do with an audit's findings, such as filing each as an issue
or posting a summary, and do it. That is not a correction: the person asked for it when they
recorded the practice, and it changes nothing in the repository.
