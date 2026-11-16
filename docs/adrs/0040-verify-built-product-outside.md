---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: 2026-11-16
supersedes: 0016
---

# Verify the built product from outside with the plugin's own agents, separately from the build

## Question

Who checks that the built product does what its accepted specs[^spec] say, and how?

## Decision

Chosen: a skill[^skill] of the plugin's own, run separately from the build[^build], in which one agent[^agent]
uses the running product from outside and gives each example[^example] a verdict with evidence,
and a second agent tries to disprove each verdict; both see only the accepted specs and the
project's practices[^practices], never the code. Only an agent that cannot read
the code has to judge the product by what it does.

## Background

[ADR 0016](0016-build-and-verify-steps.md) kept verifying out of the build and left it to a person,
with Claude Code's built-in verify skill. That skill checks a change, not the specs, and some places the plugin runs lack it, such as Claude project
threads[^thread]. The build's reviewers read the code, so a plan[^plan] whose build has finished
does not show the product works.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| A person verifies, with Claude Code's built-in skill | Rejected | Checks the change, not the specs |
| The build starts the product and checks it | Rejected | A build could then run only where the product runs |
| A lasting test suite written from each spec's examples | Rejected | Keeping tests is the build's job; this is a check after it |
| An agent that reads the code checks it against the specs | Rejected | The plugin's audit skill already compares code with specs |
| Agents that see only the specs use the product from outside | Chosen | Judges what the product does, with evidence a person can follow |

## Consequences

- Good: each requirement verified is tried on the running product.
- Good: every verdict carries what was done and what came back, so a person can judge it.
- Bad: each run costs agent time and tokens.
- Bad: verdicts can differ between runs.
- Bad: only the agents' own instructions stop them reading the code.
- Bad: nothing makes a person verify before merging, so it can be skipped.

## Out of scope

- Lasting tests that keep the product working: the build writes those.
- Releasing or deploying the product.
- Checking whether the specs ask for the right thing: that stays with the person.

## How we'll check

Applies to: the verify skill, its agents, and whether the build step starts the product.

1. Test: the skill agrees the requirements with the person before checking, and refuses uncommitted changes.
2. Test: with no recorded way to run the product, the skill checks nothing and names the practices topic to record.
3. Test: on a sample product with one broken requirement, that requirement's example fails, with evidence.
4. Test: on a sample where the agent's own helper program crashes, the example is reported not checked, never failed.
5. Inspection: the agents' instructions forbid reading code, plans and other documents; the build skill never starts the product.
6. Demonstration: on a real project, examples a build corrected now pass, without the agents reading code.

## Open questions

- None.

## Technical detail

**Which examples.** Each run first agrees with the person a list of requirements from accepted
specs: named one by one, whole specs, every accepted spec, or a plan standing for the requirements
it names. Run with nothing named, the skill proposes the requirements of the plan the branch marked
Built, if there is one. Nothing is checked until the person agrees the list. The skill then records
the commit and refuses uncommitted changes; a requirement whose spec is not Accepted is left out,
with the reason.

**Running the product.** The agents read the practices topic on running the product: machine,
start and stop commands, how to reach each interface, how to set up an example's starting state,
and what is safe to touch. When it is missing or fails, the skill stops and names
`/agentic:practices running the product`; the skill never writes it.

**Agents.** Two plugin agents, neither of which has seen the conversation, using the session's
Claude model:

- `verifier`: one per spec, run one after another; given the spec's path, the requirements to check in it, and the
  practices; may write temporary helper programs in a folder outside the repository. Verdicts:
  pass, fail, or not checked with the reason; a failure of its own helpers or setup is not checked.
- `verify-checker`: one per spec, after its verifier; repeats each pass and tries unusual inputs
  and limits, reruns each fail once, retries each not checked; says confirmed or rejected, with
  evidence. If it rejects a verdict, the report marks it disputed and leaves it to the person.

The two agents are one method: the trial below relied on the second to find the first's weak
verdicts, so they are decided together.

**Report.** Written the way the build and audit skills write theirs: a file in the plugin's data
folder, `reports/<repository>/<date>-verify-<scope>.md`, holding every agent's report copied by
script, and a reply under 150 words. The skill sets no status and changes no file in the repository.

**Evidence, from a trial on 2026-11-16.** On a mail service, 7 requirements built against an
older spec. A reading of the code beforehand expected 2 to fail. The verifier found both without
reading code, and the verify-checker confirmed them. For one passing requirement it also tried
runs cut off partway, which passed too. It flagged one passing verdict that depended on the order
in which two connections happened to open. Verifier: 29 minutes, 135,000 tokens; verify-checker:
14 minutes, 111,000.

[^build]: A build is the plugin's step that writes the code for one plan, tests first, and has it reviewed.
[^spec]: A spec is the plugin's document saying what one capability of the product should do; accepted means the person signed off its text.
[^skill]: A skill is a set of instructions Claude follows for one step, started as a slash command such as `/agentic:verify`.
[^agent]: An agent here is a separate Claude session that starts without the conversation and is given only what it needs.
[^example]: An example is one Given, When and Then case under a requirement of a spec.
[^practices]: Practices are the project's recorded ways of doing things, one topic at a time, including how to run the product.
[^thread]: A Claude project thread is one conversation inside a project in the Claude app.
[^plan]: A plan is the plugin's document for one piece of work that builds part of a spec.
