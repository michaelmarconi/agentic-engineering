# Spec rubric

Each check passes or fails. `/spec` reads this while writing; the spec reviewer reads it while
checking, and quotes the spec as evidence for every failure.

1. **Shape.** The spec has `status:` frontmatter set to Draft or Ready to build, and the sections
   Problem, Goal, Scope, Requirements, Constraints and Open questions, in that order.
2. **One specific story.** Problem names who is stuck and what happens to them today, as one
   concrete situation rather than a general complaint, and does not mention the solution.
3. **Out of scope is named.** Scope says what is out, not only what is in.
4. **What, not how.** Nothing in the spec chooses a technology, library, data structure or
   design. Such a choice belongs in an ADR, and a choice still to make is an open question.
5. **One rule per requirement.** Each requirement has a `### Requirement:` heading with a name
   unique in the spec, and exactly one rule sentence in an EARS pattern using SHALL.
6. **Scenarios add cases.** Each requirement has at least one `#### Scenario:` in Given/When/Then,
   and each scenario pins down a concrete case, such as a boundary, an error or an example with
   real values. A scenario that only restates the rule fails.
7. **Verified by.** Each requirement ends with a `Verified by:` line naming a method (test,
   demonstration, inspection or analysis) and what it checks, and the method can really be
   carried out: a test that depends on an outside system names the stand-in it uses, and
   something only a person can check is a demonstration or inspection, not a test.
8. **Testable words.** No rule or scenario relies on words that cannot be checked, such as
   "fast", "user-friendly" or "as appropriate", without a measure.
9. **Ready means ready.** A spec with status Ready to build has an empty Open questions section.
10. **No overlap.** No other spec under `docs/specs/` covers the same capability or contradicts a
    requirement here.
