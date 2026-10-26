---
name: spec
description: Write or change a spec, the living document that says what one capability of a product should do and how we will know it does, as EARS rules with Given/When/Then scenarios. Use whenever someone wants to specify, describe or pin down a feature or behaviour before building it, change what an existing feature should do, answer a spec's open questions, or mark a spec ready to build, even if they don't say "spec".
---

# Spec

A spec describes one capability of the product (something a person or another system can do
with it) as the system should behave now. It says what the system does, never how it is built,
so the code can change without the spec going stale. One capability has one spec, edited in
place; git is its history.

Before writing, read [references/rubric.md](references/rubric.md): it is the list of checks the
reviewer will apply, so writing to it saves rounds. New specs start from
[assets/template.md](assets/template.md).

## Find the spec

Specs live at `docs/specs/<capability>.spec.md`, named for the capability in lowercase with
hyphens, possibly in subfolders. Search `docs/specs/` before creating one: if a spec already
covers the capability, change it instead, because two specs for one capability will drift apart.
If `docs/brief.md` exists, read it so the spec fits the product.

## Shape it with the person

Ask one question at a time, and play back what you have understood as you go. If the person
would rather not be interviewed, draft from what they have said. Read whatever they point you
to, such as code, tickets or notes, and research what you need to: that is part of writing a
spec.

Never fill a gap with a guess. An unknown goes into Open questions, worded so it can be
answered. When the person states a technical choice (a library, a store, a design), keep the
behaviour it serves and leave the choice out: either it is already decided, in which case
suggest recording it with `/sdlc:adr`, or it is not, in which case it is an open question. When
an unknown can only be settled by trying something, suggest `/sdlc:spike`.

Write each requirement as one rule in an EARS pattern using SHALL, then scenarios that each pin
down a concrete case the rule alone leaves open: a boundary, an error, an example with real
values. End it with how we will know it holds.

## Status

The `status:` frontmatter says how far the spec is: Draft, Ready to build or Built.

- Write new and changed specs as Draft. Changing a spec that is Ready to build or Built returns
  it to Draft, because what was agreed or built no longer matches.
- Set Ready to build only when the person asks for it and Open questions is empty. If questions
  remain, say which and leave the spec as Draft.
- Never set Built. Only `/sdlc:build` does, once its review finds every requirement verified.

## Review

When the spec is written, start the `sdlc:spec-reviewer` agent and give it the spec's path; it
reads everything else it needs itself. It reports pass or fail for each rubric check with
evidence, other findings, and anything that needs the person.

Fix every finding you can and run the reviewer again, for up to ${user_config.review_rounds}
rounds in all. A finding only the person can settle, such as what a rule should be, goes to
them as a question rather than a fix you invent. If the last round still fails, stop and show
the person the report.

Finish by giving the person the spec's path and the reviewer's final report. Leave committing to
them.
