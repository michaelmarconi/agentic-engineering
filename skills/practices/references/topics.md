# Practice topics

The topics `/practices` suggests. They are not a complete list: any other topic the person asks for, such as how decisions are approved, gets a topic file and a line in the core in the same way. The overview shows each topic as recorded, not recorded yet or out of step with the repository, and suggests the one that matters most now. Within a topic, it reads the repository first, proposes what
it finds, and asks only what it cannot find. Where an answer is long, it goes in a topic file;
otherwise it is a line in the core. A choice between alternatives goes to `/adr`.

| # | Topic | Asks | Usually ends up |
|---|---|---|---|
| 1 | Setting up | What a fresh copy needs: tools, services such as a database, local config; any machine or operating system the work needs; where secrets live; the command that sets it up and the one that runs the product | Check your work, Rules |
| 2 | Checking work | The exact commands: all tests, one test file, lint and format, type check; which ones run before every commit | Check your work, Rules |
| 3 | Testing | Test-first or not; what each change must be tested with; coverage and any minimum; end-to-end tests and when they run; test data; what to do with a flaky or slow test | Rules (test-first), `testing.md` |
| 4 | Branches and commits | Branch names; commit message style; whether work may be committed straight to the default branch | Rules |
| 5 | Reviews and merging | Pull requests or not; who reviews; how work is merged; what must pass before merging | Rules, or `merging.md` |
| 6 | CI/CD | Where the pipeline is defined and what it runs on each push, pull request and release; if there is none yet, what it must run (which service to use is an ADR); how to run the same checks locally before pushing; when a run fails: read its log, reproduce the failure locally and fix the cause, re-run at most once and only to rule out a fault outside the change, never skip or disable a test to get green; who may change the pipeline files, and whether agents may; how deployments are triggered and by whom | `ci.md`, Rules |
| 7 | Releasing and deploying | Version numbers and changelog; how a release is made and by whom; environments; rolling back | `releasing.md` |
| 8 | Database changes | How they are written and applied; whether they must be reversible | `database-changes.md` |
| 9 | Security and dependencies | Before adding a dependency: what to check (kept up to date by its authors, widely used, licence, the exact name, to avoid look-alike packages) and who agrees it; if the project has a lock file, that it is committed and installs use only it; the command that scans dependencies for known holes, and when it runs; how and how often dependencies are updated; secret scanning; what to do on finding a security hole, such as never describing it in a public issue or commit message | `security.md` |
| 10 | Hands off | Files and folders an agent must never edit, such as generated code; actions it must never take, such as running a script that changes shared data | Rules |
| 11 | Documents to keep up to date | Which documents must change with the code | Rules |

Left out on purpose: anything for people only, such as how to report a bug.
