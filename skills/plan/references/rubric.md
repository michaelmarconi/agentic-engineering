# Plan rubric

Each check passes or fails. `/plan` reads this while writing; the plan reviewer reads it while
checking, and quotes the plan as evidence for every failure.

1. **Shape.** The file is `docs/plans/YYYY-MM-DD-<title-in-lowercase-with-hyphens>.md`, directly
   in that folder. Its frontmatter has `type: Plan`, `status:` set to `📝 Draft`, `🟢 Ready to build` or
   `✅ Built`, emoji included, and `date:` as YYYY-MM-DD if it has one (a missing date passes: a plugin hook requires it with the next
   status change). Under a `# ` title, the sections are Specs, ADRs, Decisions, Plan
   and Open questions, in that order, and no `<!-- -->` comment from the template is left in; the
   frontmatter's `#` line stays.
2. **Specs.** Each entry under Specs is a reference to a spec under `docs/specs/`, by its title
   and path, with at least one requirement nested beneath it as `  - [<name>](<path>#<anchor>)`:
   a link to the same spec whose text is the name of a numbered requirement heading in that
   spec, as `### 2. <name>`, word for word and without its number, and whose anchor is the one
   GitHub gives that heading, as `#2-<name-in-lowercase-with-hyphens>`. Specs says "None." only
   when ADRs lists at least one ADR, so the plan always builds something.
3. **ADRs.** ADRs is a `| ADR | Decision |` table with one row per ADR, its number linking to an
   ADR under `docs/adrs/` that exists and its title, word for word, as the decision; or the
   section says only "None."
4. **Settled.** Each spec and each ADR listed is `👍 Accepted`.
5. **Decisions.** Decisions holds one line for each decision, saying what was decided and why, or
   only "None." Take the lines one at a time. A line that only follows what a listed spec, ADR or
   the practices already say, or a pattern the code already uses, needs nothing recorded and
   passes. Ask of every other line these questions in order, stopping at the first yes. A yes to
   1, 2 or 3 fails the line, naming where it belongs, and it is an open question until that
   document holds it. A yes to 4 passes if the line says `/build` leaves the reason as a comment
   beside the code, and otherwise fails, asking for that sentence. A yes to 5 passes.

   1. **Must later work follow it?** Other code, written by later plans, has to do the same thing
      or use the same thing: a library every module calls, the format of a stored field, a test
      set-up later tests reuse. It belongs in an **ADR**.
   2. **Does a user or caller rely on it?** Someone outside the code sees or depends on it: the
      columns of an export file, the wording of an error a user reads, what an interface accepts
      and returns, what happens to bad input from outside. It belongs in **the spec**.
   3. **Does every later piece of work do it this way?** It is how people and agents work on the
      project rather than what the code does: a branch naming rule, a command run before every
      commit, who signs off a release. It belongs in **the practices**.
   4. **Would someone changing this code later need the reason?** Without it, they might undo the
      choice and break something: a cache kept small to fit a device's memory, a sort kept stable
      on purpose. It belongs in **a comment beside the code**.
   5. **Otherwise nobody needs the reason once the work is built**: the order of the steps, the
      names of local variables, which file a helper goes in.

   Judge what the decision does, not how important it sounds, and not whether its wording says
   "from now on". A line about this work alone can still answer yes to question 1 or 2.
6. **No hidden decisions.** The Plan section makes no technical decision missing from Decisions
   and ADRs: a choice with a reasonable alternative that the specs, the ADRs, the practices and
   the existing code do not already settle. Following a pattern the code already uses is not a decision. A
   case you cannot judge from the page goes under Needs a person.
7. **No code.** The Plan section holds no code: no code blocks other than `mermaid` diagrams, as
   check 13 says, and no lines of code, though it may name files, functions and commands.
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

13. **Diagrams match the text.** A diagram is a `mermaid` block in the Plan section, after its
    opening paragraph and before the steps. Every box, arrow and label in it names something the
    plan's text already says, so the diagram makes no decision and states no fact of its own; quote
    each one the text does not hold. A plan with no diagram passes.

The reviewer also passes on this advice for the Plan section as suggestions, never as
failures: start with why the work is being done and what it leaves for later; give one
recommended approach, not the alternatives; name the files that matter and the code to reuse;
keep it short enough to scan but detailed enough to carry out.
