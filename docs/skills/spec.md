# `/spec`

`/spec` is the skill for writing and changing specs. It is one step of
[the SDLC](../../README.md); read that page first for the documents, skills and agents it
mentions.

## What a spec is

A spec describes one capability of the product: something a user or another system can do
with it, such as resetting a password. There is one spec per capability, and it describes the
system as it should behave now. It says
*what* the system does, never *how* it is built: a technical choice that comes up while shaping
a spec belongs in a [spike](../../README.md#spike) or an [ADR](../../README.md#adr).[^openspec]
A spec is edited in place on a branch, and git is its history.

## Anatomy

| Section | Holds |
|---|---|
| Problem | Who is stuck, and what happens today, told as one specific story[^shapeup] |
| Goal | What changes for them when this is built |
| Scope | What is in, and what is explicitly out[^shapeup] |
| Requirements | The behaviour, one requirement at a time |
| Constraints | Hard limits the behaviour must respect |
| Open questions | Unknowns still to answer; empty before the spec can be Ready to build |

Each requirement has a name, one rule and some scenarios. The rule is a single sentence in
EARS, a small set of sentence patterns for requirements such as "IF ..., THEN the system SHALL
...", where SHALL means the requirement is mandatory.[^ears][^rfc2119] The scenarios use
Gherkin's Given/When/Then, the format behaviour-driven development uses to describe one
example.[^gherkin] The rule covers every case; each scenario pins down one concrete case of it,
such as a boundary or an example with real values, and never adds an outcome the rule does not
state. A scenario that only restates the rule is left out.[^openspec] *Verified by* names the method that shows the requirement holds: usually a
test, otherwise a demonstration, inspection or analysis.[^nasa]

```markdown
### Requirement: Reset links expire

IF a reset link is more than 24 hours old, THEN the system SHALL reject it.

#### Scenario: Link used just before expiry
- GIVEN a reset link issued 23 hours 59 minutes ago
- WHEN the user opens it
- THEN the system lets them set a new password

#### Scenario: Link used just after expiry
- GIVEN a reset link issued 24 hours 1 minute ago
- WHEN the user opens it
- THEN the system rejects it and offers to send a new one

Verified by: unit tests for both scenarios.
```

## Lifecycle

```mermaid
stateDiagram-v2
    direction LR
    [*] --> Draft
    Draft --> Ready: ready
    Ready --> Draft: change
    Ready --> Built: built
    Built --> Draft: change
    Ready: Ready to build
```

- **Draft:** being shaped.
- **Ready to build:** you have said it is done, Open questions is empty, and the review
  (below) has passed with no decision left for you.
- **Built:** the last [`/build`](../../README.md#build) review found every requirement in the
  spec verified, however many plans it took to build them.

Changing a Ready or Built spec returns it to Draft. A capability that is no longer wanted has
its spec deleted; git keeps the history.[^openspec]

Three things keep specs in this shape:

- **Review.** Before you see a spec, `/spec` has its reviewer agent check it against a short
  list of pass-or-fail checks: the sections are all there, each requirement has one EARS rule,
  its scenarios add real cases, and Verified by names a method. `/spec` fixes what the reviewer
  finds and has it checked again, up to the number of reviews in the Review rounds setting (see
  [Install](../../README.md#install)), then you get the spec with the final report. If that
  setting has not been saved, `/spec` stops before the first review and asks you to save it.
- **Status.** A hook checks each edit Claude makes to a spec with its file-editing tools and
  refuses one the lifecycle does not allow: a new spec that is not Draft, Ready to build while
  Open questions is not empty, setting Built, or a change to a Ready to build or Built spec that
  does not return it to Draft. Built is refused for now because only `/build` may set it, after
  its own review passes, and `/build` is not built yet. Plans will get the same kind of check
  when `/plan` is built.
- **Audit.** [`/audit`](../../README.md#audit) finds specs and code that no longer agree, such
  as after a spec was edited by hand, which the hook does not see.

## Using `/spec`

Run `/spec` and tell it what you want to do:

- **New:** start a spec for a capability. `/spec` first checks whether an existing spec already
  covers it.
- **Change:** edit a spec in place, including answering an open question.
- **Ready:** mark a spec Ready to build.

## Where specs live

`docs/specs/<capability>.spec.md`, named for the capability. Specs start flat; when there are
enough to need it, group them into folders of your choosing. The plugin finds specs anywhere
under `docs/specs/` and gives folders no meaning. Move a spec with `git mv`, which keeps its
status; the hook would see a spec written in a new place as a new spec and require Draft.

[^ears]: Mavin, Wilkinson, Harwood and Novak, "Easy Approach to Requirements Syntax (EARS)",
    17th IEEE International Requirements Engineering Conference, 2009,
    [doi:10.1109/RE.2009.9](https://doi.org/10.1109/RE.2009.9); summary on
    [Wikipedia](https://en.wikipedia.org/wiki/Easy_Approach_to_Requirements_Syntax). We take its
    sentence patterns for each requirement's rule.
[^gherkin]: Cucumber, [Gherkin reference](https://cucumber.io/docs/gherkin/reference/). We take
    Given/When/Then for scenarios, without requiring a test runner.
[^openspec]: Fission AI, [OpenSpec: Writing Good Specs](https://github.com/Fission-AI/OpenSpec/blob/main/docs/writing-specs.md).
    We take its rule that a spec describes behaviour, not code; its requirement and scenario
    headings; its rule that a scenario must exercise its requirement rather than restate it;
    and deleting a capability's spec when it is retired. We leave out its change folders and
    delta specs.
[^rfc2119]: Bradner, [RFC 2119: Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/info/rfc2119/),
    1997.
[^nasa]: NASA, [Systems Engineering Handbook, 5.3 Product Verification](https://www.nasa.gov/reference/5-3-product-verification/).
    We take its four verification methods: test, demonstration, inspection and analysis.
[^shapeup]: Ryan Singer, [Shape Up, chapter 6: Write the Pitch](https://basecamp.com/shapeup/1.5-chapter-06),
    Basecamp, 2019. We take its Problem, told as one specific story, and its no-gos, things
    explicitly excluded, which become our out of scope.
