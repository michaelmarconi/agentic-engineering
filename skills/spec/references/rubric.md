# Spec rubric

Each check passes or fails. `/spec` reads this while writing; the spec reviewer reads it while
checking, and quotes the spec as evidence for every failure.

1. **Shape.** The spec's frontmatter has `type: Spec`, `status:` set to `📝 Draft` or `👍 Accepted`,
   emoji included, `date:` as YYYY-MM-DD (a document written before dates may have none until its status next changes) and the
   template's `#` line, and at least the sections
   Story, In scope, Out of scope, Requirements,
   Constraints and Open questions, in that order relative to each other. Further sections, such
   as "Security" or "Privacy", may go wherever they fit before Open questions, which comes last,
   and every other check applies to them too. A further section holds no numbered requirement
   heading; those belong under Requirements.
2. **One story.** Story is one sentence, "When <situation>, <who> wants to <do something>, so
   they can <outcome>.", naming a concrete situation rather than a general complaint, and an
   outcome someone can see. It uses only people the person named, and does not choose how the
   capability works, not even in passing, such as the file format, screen or button it will use.
   While the person has not given the situation, who it is or the outcome, a Story that says what
   is not known yet, with Open questions asking for it, passes.
3. **Out of scope is named.** Out of scope names at least one thing the capability will not do.
   While the person has not said what is out, an Out of scope section that says so, with Open
   questions asking what is out, passes; "anything not stated is undecided" alone does not.
4. **What, not how.** Nothing in the spec chooses a technology, library, data structure or
   design. Such a choice belongs in an ADR, and a choice still to make is an open question. Nor is
   a rule's subject an internal step, such as what the system stores, calls or works out on the
   way: each rule states something a person or another system can see the system do.
5. **One rule per requirement.** Each requirement is a heading `### <number>. <Name>` under
   Requirements, numbered 1, 2, 3 and so on in order with none missed, with a name unique in the
   spec, and has exactly one rule sentence in an EARS pattern, using SHALL once.
6. **Examples add cases.** Each requirement has at least one example: a two-column table whose
   header row is `| Example | <name> |`, then a Given, a When and a Then row, with And rows after
   any of them. Exact text, such as a message the system shows or an email address, is in
   backticks. Each example pins down a concrete case, such as a
   boundary or a case with real values. Where a rule has a limit, such as a time or a count,
   examples sit just on each side of it, and the spec's rules state the outcome on both sides
   (one rule may cover both, as in "SHALL accept the link if it is at most 24 hours old, and
   reject it otherwise"). Example values name no person except people the person named:
   otherwise use generic ones such as `user@example.com`. An example that only restates the rule
   fails. So does one whose outcome no rule in the spec states, such as what happens on an error
   or when a rule's condition does not hold: until the person decides that case, it is an open
   question, or a rule is widened to state it.
7. **How we'll check.** Each requirement ends with a `#### How we'll check` heading, under which
   the spec names a method (test, demonstration, inspection or analysis) and what it checks, and
   the method can really be carried out: a test that depends on an outside system names the
   stand-in it uses, and something only a person can check is a demonstration or inspection, not
   a test.
8. **Testable words.** No rule, example or constraint relies on words that cannot be checked,
   such as "fast", "user-friendly" or "as appropriate", without a measure.
9. **Accepted means settled.** A spec with status `👍 Accepted` has no open questions: its
   Open questions section is empty or says only "None."
10. **No overlap.** No other spec under `docs/specs/` covers the same capability or contradicts a
    requirement here.
11. **References.** The spec does not refer to the brief, another spec, an ADR, a plan or a spike
    record in any way: no hyperlink, path or title. Those can change or be deleted without this
    spec being touched, so the reference would go stale. A spike's finding is stated in the spec's
    own words, with its evidence. The spec refers to outside material only by a web link. It never
    refers, by hyperlink, path or title, to material handed over in the conversation, to anything
    outside the repository, or to a file under `docs/` that is not a brief, spec, ADR, plan or
    spike record: such material can change or vanish without the spec being touched, so what
    matters from it is stated in the spec's own words. References to code are not part of this
    check.
12. **Outcome first.** Requirement 1 states the outcome the Story asks for, as something someone
    can see, and its How we'll check checks that outcome. The other requirements say how the
    outcome holds in particular cases, such as who receives something or what happens when it
    cannot be done.
13. **One capability.** The spec covers one capability: every requirement serves the Story's one
    outcome. A requirement that serves an outcome someone could ask for on its own, such as
    exporting what another requirement imports, fails: it belongs in a spec of its own.
14. **Proposed answers.** Each open question ends with "Proposed:" and the answer the writer
    would choose, so the person can accept it in a word or give another. A question only the
    person can answer, such as who the Story is about, proposes no guess: its "Proposed:" says what
    would settle it, such as "tell me who asked for this and what happens to them today". A default
    the person did not give is never stated as a rule: it is an open question with that default
    proposed.
