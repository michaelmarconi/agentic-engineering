# Build rubric

Each check passes or fails. `/build` reads this before it builds; the build reviewer reads it
while checking the build, and quotes the code, a test or the git log as evidence for every
failure. "The build" is every commit on the branch that the default branch does not have.

1. **Every requirement built.** For each requirement the plan names, the code does what its rule
   says, in every case the rule covers, not only the cases its scenarios show.
2. **Each scenario tested.** For each requirement whose Verified by line names a test, each of its
   scenarios has a test that sets up the scenario's GIVEN, does its WHEN and checks its THEN, with
   the scenario's own values, as the spec words them. A test that checks less, such as only that
   no error is raised, fails. For a requirement verified by inspection or analysis, the code
   shows what that line says it checks. A requirement verified by demonstration needs no test:
   it is left for the person to check after the build, and is not a failure.
3. **Tests first.** For each requirement, its tests were committed before the code that makes
   them pass, or in the same commit; no commit adds code for a requirement whose tests come later.
4. **No test weakened.** No test that existed before the build, or that an earlier commit of the
   build added, was changed to check less: no assertion removed or loosened, no expected value
   changed to match the code, no test skipped, disabled or deleted. Changing a test to check its
   scenario more closely is fine, and so is correcting an expected value that plainly contradicts
   its scenario in the spec to the spec's value, when the summary says so.
5. **Nothing unrequested.** The build adds no behaviour that neither a named requirement, nor the
   Plan section, nor what those need to work, asks for. Correcting an obvious defect that no spec
   mentions, such as a crash, an unhandled error or bad input that is not refused plainly, is not
   new behaviour.
6. **ADRs followed.** The code follows each ADR the plan lists, and each other `👍 Accepted` ADR
   whose Confirmation section says it applies to the code the build changes.
7. **Plan followed.** The code follows the Plan section and each line under Decisions. Where it
   departs from them, the departure is a choice rubric check 8 allows `/build` to make itself.
8. **No choice made quietly.** The build makes no choice that would need an ADR or a change to a
   spec: a lasting choice between real alternatives, such as a library, a data format or the
   shape of an interface, that no listed ADR, spec, Decisions line or existing code already
   settles; a change to what a user sees that the spec does not settle, other than the wording of
   error messages, exit codes and sensible handling of odd input; something hard to undo,
   such as a database schema, a public interface or data already stored; or anything that
   stretches or contradicts a spec, an ADR or the project's practices. Names, how the code is
   split up and which helper to use are `/build`'s to choose, and so is correcting an obvious
   defect, unless what should happen instead is a real product choice that a reasonable person
   could want made differently, and so is any choice that is easy to change later, when the summary lists it.
9. **Documents untouched.** The build changes no spec, ADR or brief, and changes the plan only to
   set its status.

A finding about tidiness or style is a suggestion, never a failure.
