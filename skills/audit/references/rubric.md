# Audit rubric

Each check passes or fails. `/audit` reads this before it runs; the skill's evals assert each
check. "The run" is one `/audit` from the person's request to its findings.

1. **Script first.** The run starts with the audit script's `documents` command, and, for a
   window, its `window` command. Every problem `documents` reports appears among the findings,
   with the document it names. A refused script run, or one Claude Code doesn't allow, ends the
   run with its reason.
2. **Stops when it must.** A window the script refuses, or a named document that doesn't exist or
   isn't `👍 Accepted`, ends the run with its reason before anything is checked, documents
   included. No lifecycle documents, no accepted spec or ADR, or a window with no commits is said
   plainly; the document checks still run in the last two cases.
3. **One auditor per document in scope.** Each `👍 Accepted` spec and ADR in scope gets exactly
   one `sdlc:auditor` agent, and no other document gets one: no `📝 Draft` spec or ADR, no
   `❌ Rejected` or `↪️ Superseded` ADR, no plan, spike record or brief. In scope is every accepted
   spec and ADR; for a window, those the `sdlc:audit-picker` agent picks plus those whose own text
   changed; for a named document, that one.
4. **All at once.** Every auditor is started in one message. Any refused for Claude Code's limit
   on agents running at once is started again once the others have reported, and none is left
   unchecked.
5. **Findings quote both sides.** Each drift finding quotes the requirement or decision and the
   code, with its file and line, as the auditor reported them.
6. **Drift is checked.** Each document whose auditor reported drift gets one `sdlc:audit-checker`
   agent, after its auditor has reported; a document with no drift gets none. Only confirmed
   findings are reported as drift. Each rejected one is listed with the checker's reason.
7. **Order.** Findings come in this order, grouped by document within each part: drift, problems
   with the documents, requirements not built yet (per spec, the count and names), ADR checks
   that need a run (with what to run), documents to consider deleting (`✅ Built` plans and
   finished spike records), unfinished spike records with their dates, and rejected findings. A
   part with nothing in it is left out.
8. **Each correction named.** Each drift finding and each problem with a document names its
   suggested correction and the skill that makes it: correct the code, through `/plan` and
   `/build` or directly when small; return the spec to `📝 Draft` and change it, through `/spec`;
   supersede the ADR, through `/adr`; or, for a problem with a document, the edit that corrects
   it.
9. **Changes nothing.** The run writes, edits and deletes nothing in the repository, sets no
   status, and makes no commit.
