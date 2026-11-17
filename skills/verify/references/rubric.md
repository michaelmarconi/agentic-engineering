# Verify rubric

Each check passes or fails. `/verify` reads this before it runs; the skill's evals assert each
check. "The run" is one `/verify` from the person's request to its reply.

1. **Script first.** The run starts with the verify script's `start` command, before any agent.
   A refusal, such as for uncommitted changes, or a run Claude Code doesn't allow, ends the run
   with its reason and nothing checked.
2. **Agreed first.** Before any agent starts, the run shows the list it will check: each spec
   with its requirements and how many examples they hold, as `start` lists them, and any
   requirement left out because its spec is not `Accepted 👍`, with that reason. No agent starts
   until the person agrees in this conversation. A request that names the requirements, whole
   specs, every accepted spec or a plan, and says to go ahead, is that agreement.
3. **Practice first.** Before any agent starts, the run reads the Running the product practice.
   When there is none, no agent starts and the reply names `/agentic:practices running the
   product`. When it names a machine or operating system this session is not running on, no
   agent starts and the reply says why. The run never writes or changes the practice.
4. **One verifier, then one checker, per spec.** Each spec in the agreed list gets exactly one
   `agentic:verifier` agent, then, once it has reported, one `agentic:verify-checker` agent given
   that report word for word. Specs are checked one after another, never side by side. Each
   request starts with the spec's full path on a `Document:` line and the repository on a
   `Repository:` line, then names only the agreed requirements of that spec. No request holds
   code, tests, a plan, another document or the conversation.
5. **Every example has a verdict.** Each example of each agreed requirement is reported as pass,
   fail or not checked. A pass or fail carries evidence: what was done to the product and what
   came back. A not checked carries its reason and what would make it checkable. A failure of an
   agent's own helper or setup is not checked, never fail.
6. **Only confirmed verdicts stand.** A verdict the checker confirmed stands. One it rejected is
   reported as disputed, with both agents' evidence, for the person to decide. A spec whose
   verifier or checker reported an `Error:` is reported as not checked, never as passed.
7. **Each failure names its next step.** Each failed verdict names one: correct the code, through
   `/plan` and `/build` or directly when small; or return the spec to `Draft 📝` and change it,
   through `/spec`, when the product is right and the spec is not.
8. **The report holds it all.** The report file is written by the script's `report` command, with
   the commit `start` printed and the overall result, then the failed, disputed, not checked and
   passed verdicts, in that order, grouped by spec.
9. **Short reply.** The reply is under 150 words: the outcome, at most five bullets of at most 15
   words each, and the report file's full path. It never pastes the report.
10. **Changes nothing.** The run writes, edits and deletes nothing in the repository, sets no
    status and makes no commit. It never reads the code or tests itself to judge a verdict.
