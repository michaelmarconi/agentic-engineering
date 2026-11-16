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
uses the running product through its interfaces, as a person would, and gives each example[^example]
a verdict with evidence, and a second agent tries to disprove each verdict. Both are given only the
accepted specs and the project's practices[^practices], and told never to read the code, so they
must judge the product by what it does. Both run on Sonnet, like the plugin's other agents.

## Background

[ADR 0016](0016-build-and-verify-steps.md)[^adr] kept verifying out of the build and left it to a person,
with Claude Code's built-in verify skill. That skill checks a change, not the specs, and Claude project
threads[^thread] lack it. The build's reviewers read the code, so a plan[^plan] whose build has finished
does not show the product works.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| A person verifies, with Claude Code's built-in skill | Rejected | Checks the change, not the specs |
| The build starts the product and checks it | Rejected | A build could then run only where the product runs |
| A lasting test suite written from each spec's examples | Rejected | Lasting tests are the build's job |
| An agent that reads the code checks it against the specs | Rejected | The plugin's audit skill[^audit] does this |
| Agents that see only the specs use the running product | Chosen | Judges what the product does, with evidence a person can follow |

## Consequences

- Good: each requirement[^requirement] the person agrees to verify is tried on the running product, at a recorded commit.
- Good: every verdict carries evidence or a reason a person can judge.
- Bad: specs are checked one after another, since each check starts and stops the product.
- Bad: verdicts can differ between runs.
- Bad: only the agents' own instructions stop them reading the code.
- Bad: a person can skip verifying before merging.

## Out of scope

- Lasting tests: the build writes those.
- Releasing or deploying.
- Checking ADRs: the audit skill checks them against the code.
- Checking whether the specs ask for the right thing: that stays with the person.

## How we'll check

Applies to: the verify skill, its agents, and whether the build step starts the product.

1. Test: the skill agrees the requirements with the person before checking, and refuses uncommitted changes.
2. Test: with no recorded way to run the product, the skill checks nothing and names the practices topic to record.
3. Test: on a sample product with one broken requirement, that requirement's example fails, with evidence.
4. Test: on a sample where the agent's own helper program crashes, the example is reported not checked, never failed.
5. Inspection: the agents' instructions forbid reading code, plans and other documents; the build skill never starts the product.
6. Demonstration: on a real project, examples a build corrected now pass, and the agents' recorded commands read no code.

## Open questions

- None.

## Technical detail

**Which examples.** Each run first agrees with the person a list of requirements from accepted
specs: named one by one, whole specs, every accepted spec, or a plan standing for the requirements
it names. Run with nothing named, the skill proposes the requirements of the plan whose build the branch
finished, if there is one. A requirement whose spec is not Accepted is left out,
with the reason.

**Running the product.** The agents read the practices topic on running the product: machine,
start and stop commands, how to reach each interface, how to set up an example's starting state,
and what is safe to touch. When it is missing or fails, the skill stops and names
`/agentic:practices running the product`; the skill never writes it.

**Agents.** Two plugin agents, neither of which has seen the conversation, set to always
run on the Sonnet model, like the plugin's other agents, so cost and quality of judgement match theirs:

- `verifier`: one per spec, run one after another; given the spec's path, the requirements to check in it, and the
  practices; may write temporary helper programs in a folder outside the repository. Verdicts:
  pass, fail, or not checked with the reason; a failure of its own helpers or setup is not checked.
- `verify-checker`: one per spec, after its verifier; repeats each pass and tries unusual inputs
  and limits, reruns each fail once, retries each not checked; says confirmed or rejected, with
  evidence. If it rejects a verdict, the report marks it disputed and leaves it to the person.

The two agents are one method: the trial below relied on the second to find the first's weak
verdicts, so they are decided together.

**Report.** Written the way the build and audit skills write theirs: a file in the plugin's data
folder[^data], `reports/<repository>/<date>-verify-<scope>.md`, holding every agent's report copied by
script, and a short reply. The skill sets no status and changes no file in the repository.

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
[^adr]: An ADR (architecture decision record) is a document recording one technical decision and why it was made.
[^requirement]: A requirement is one rule in a spec that the product must meet, with its examples.
[^data]: The plugin's data folder is a folder Claude Code gives each plugin in the person's home folder, outside every repository.
[^audit]: The audit skill is the plugin's step that checks the code against the accepted specs and ADRs, reading the code and running nothing.
[^plan]: A plan is the plugin's document for one piece of work that builds part of a spec.
