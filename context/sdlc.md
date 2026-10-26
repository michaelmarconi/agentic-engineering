This repo follows the sdlc plugin's lifecycle. Use its skills, invoked as /sdlc:<name>, for
each step that has one; some steps' skills are not built yet, and only those Claude Code lists
exist.

Steps: /brief (whole product), then /spec (one capability). /spike settles an unknown by
experiment when needed: a fact goes back into the spec, a choice becomes an ADR. /adr records one
technical decision. /plan scopes a piece of work; /build builds, reviews and merges it. /audit
finds drift (code and documents that disagree) at any time.

Documents and statuses (the `status:` field in each document's frontmatter):
- Brief, `docs/brief.md`: what the product is, for whom and why.
- Spec, `docs/specs/**/<capability>.spec.md`: Draft → Ready to build → Built; a change returns it to Draft.
- ADR, `docs/decisions/`: Proposed → Accepted or Rejected; Accepted → Superseded.
- Plan, `docs/plans/`: Draft → Ready to build; /build deletes it in the commit that merges its work.

Principles:
- Specs say what the system does, never how. A technical choice is an ADR.
- One living spec per capability, edited in place. Git is the history; a retired spec is deleted.
- One decision per ADR. An accepted ADR is never edited, only superseded whole.
- Accepted ADRs and the code are the design; there is no separate design document.
- Every spec, ADR and plan carries its own status. A plan holds no state that would be lost when it is deleted.
- Only legal status moves are allowed, and only /build sets Built. A plugin hook refuses illegal
  spec status changes made with Claude's file-editing tools.
- A spec is Built when /build's spec reviewer finds every requirement in the whole spec verified,
  not just the plan's part. /audit repeats that judgement later.
- A plan is Ready to build only when each spec it touches is Ready to build or Built, and each
  ADR it touches is Accepted.
- Every document a skill writes is reviewed by that skill's reviewer agent before a person sees
  it. Findings are fixed for up to n rounds (a plugin setting, 3 by default); only decisions go to the person.
- Drift is a finding, not a status: report it with a suggested way back.
