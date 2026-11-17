# Release notes rubric

Each check passes or fails. `/release` reads this while drafting the notes; the release reviewer
reads it while checking, and quotes the notes as evidence for every failure.

1. **Everything covered.** Every note listed under `=== NOTES GATHERED ===` in the request, and
   every item listed under `=== FROM HISTORY ===`, appears in the notes, reworded or merged with
   another where they describe the same thing. Nothing gathered is left out, except what is listed
   under `=== LEFT OUT ===`, which the person chose to leave out and the notes must not hold.
2. **Nothing invented.** Every statement in the notes says what a gathered note or a history item
   says, or less. A feature, fix, number or promise that none of them gives fails, and so does a
   history item described as more than its subject line says.
3. **For the people who use the product.** Each item says what users can now do, or what changed
   for them, in plain words. An item that describes code instead, such as "refactored the parser"
   or "added a test", fails; work that changes nothing for users is left out only
   when the person said so, which `=== LEFT OUT ===` then lists.
4. **Nothing internal.** The notes name no plan, spec, ADR, branch or file path of the project,
   no commit hash and no function, class or module names, unless the product's users work with
   that name themselves, such as a command they type.
5. **Recorded form.** The notes follow the form under `=== FORM ===` in the request, such as a
   Keep a Changelog entry headed `## [1.4.0] - 2026-11-17` with `### Added` and `### Fixed`
   sections. When the request says no form is recorded, the notes are a heading naming the
   version, then a list of short items, which passes.
6. **Version.** The version in the notes is the one on the request's `Version:` line, and the
   notes name it once.
