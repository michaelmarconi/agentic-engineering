# Plan rubric

Each check passes or fails. `/plan` reads this while writing; the plan reviewer reads it while
checking, and quotes the plan as evidence for every failure.

1. **Shape.** The file is `docs/plans/YYYY-MM-DD-<title-in-lowercase-with-hyphens>.md`, directly
   in that folder. Its frontmatter has `type: Plan`, `status:` set to `📝 Draft`, `🟢 Ready to build` or
   `✅ Built`, emoji included, and `date:` as YYYY-MM-DD. Under a `# ` title, the sections are Specs, ADRs, Decisions, Plan
   and Open questions, in that order, and no `<!-- -->` comment from the template is left in; the
   frontmatter's `#` line stays.
2. **Specs.** Each entry under Specs is a reference to a spec under `docs/specs/`, by its title
   and path, with at least one `- Requirement: <name>` line beneath it, and each name is the
   name of a numbered requirement heading in that spec, as `### 2. <name>`, word for word and
   without its number. Specs says "None." only when ADRs
   lists at least one ADR, so the plan always builds something.
3. **ADRs.** Each entry under ADRs is a reference to an ADR under `docs/adrs/` that exists, by its
   number, title and path, or the section says only "None."
4. **Settled.** Each spec and each ADR listed is `👍 Accepted`.
5. **Decisions.** Decisions holds one line for each decision, saying what was decided and why, or
   only "None." No line is a decision that later work must follow: that needs an ADR, so it is an
   open question until the ADR is `👍 Accepted` and listed under ADRs.
6. **No hidden decisions.** The Plan section makes no technical decision missing from Decisions
   and ADRs: a choice with a reasonable alternative that the specs, the ADRs and the existing
   code do not already settle. Following a pattern the code already uses is not a decision. A
   case you cannot judge from the page goes under Needs a person.
7. **No code.** The Plan section holds no code: no code blocks and no lines of code, though it
   may name files, functions and commands.
8. **References.** The plan refers only to the specs and ADRs it lists, and to files in the code.
   It does not refer to the brief, to another plan or to a spike record in any way: no
   hyperlink, path or title. It refers to outside material only by a web link, never to material
   handed over in the conversation, to anything outside the repository, or to a file under
   `docs/` that is not a brief, spec, ADR, plan or spike record: what matters from such material
   is stated in the plan's own words.
9. **Ready means ready.** A plan with status `🟢 Ready to build` or `✅ Built` has an Open
   questions section that is empty or says only "None."
10. **No overlap.** No other plan under `docs/plans/` that is `📝 Draft` or `🟢 Ready to build`
    names a requirement that this plan names.
11. **Fits the practices.** Where the project's practices say how work is split or how big one
    plan may be, the plan keeps to them, or Decisions has a line saying the work was kept whole
    and why. With no such practice, this passes. Only the person can choose between splitting a
    plan that fails and keeping it whole, so that choice also goes under Needs a person.
12. **Proposed answers.** Each open question ends with "Proposed:" and the answer the writer
    would choose, such as the decision an ADR to record should make, so the person can accept it
    in a word or give another. A question only the person can answer proposes no guess: its
    "Proposed:" says what would settle it.

The reviewer also passes on this advice for the Plan section as suggestions, never as
failures: start with why the work is being done and what it leaves for later; give one
recommended approach, not the alternatives; name the files that matter and the code to reuse;
keep it short enough to scan but detailed enough to carry out.
