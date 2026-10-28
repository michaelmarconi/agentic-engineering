# `/build`

*Not built yet.*

A build agent carries out the plan, then four reviewer agents check the result in parallel:

- **Code:** is it correct and well made?
- **Security:** does it open any holes?
- **Spec:** is everything the plan was for built and shown to work, with nothing unrequested
  added? Once every requirement in the spec is, the spec is marked Built.
- **ADRs:** is every accepted decision followed, not just the ones the plan touches?

Findings follow the same [review process](../lifecycle.md#review-process) as documents: the build
agent corrects them once, then a correction check asks whether each correction was made and
nothing broke. A clean review or a passing correction check merges the work into the main branch;
a failing correction check stops and asks for help.

TODO: the code and security reviews are Claude Code's own built-in reviews.
