---
# Change status only through the agentic plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
number: 0054
status: Accepted 👍
date: 2026-11-20
supersedes: 0026
---

# Allow links from lifecycle documents only to each other and the web

## Question

Which links into the repository may the lifecycle's documents[^lifecycle] hold?

## Decision

Chosen: the hook[^hook] refuses any new link from a lifecycle document into the repository unless
it leads to another lifecycle document, so these documents link only to each other and to the web.
Anything else in the repository, code included, can be renamed, moved or deleted without the
document being edited, and one rule for every target is simpler to follow.

## Background

[ADR 0026](0026-outside-material-references.md) has the hook refuse links to outside material,
including files under `docs/` that are not lifecycle documents, while links to code and folders
pass. The lifecycle gives as its reason that `docs/` holds only the lifecycle's documents. That is
not true: a project may keep other pages there, and the plugin itself writes the project's working
rules, such as how it tests, branches and releases, in a folder of its own there. The same reason,
that the target can change without the document being edited, holds just as well for code, which is
let through.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Allow links to any file in the repository | Rejected | Other pages under `docs/` may be short-lived, and a link to one can stop being correct without anyone noticing |
| Keep refusing other `docs/` files and allow code | Rejected | No reason tells the two apart: both can change without the document being edited |
| Allow links only to other lifecycle documents and the web | Chosen | One rule for every target; a file can still be named in plain text, and nothing a link may reach can become out of date by itself |

## Consequences

- Good: a lifecycle document cannot gain a link that breaks when code or another page moves.
- Good: other files may live under `docs/`, and the lifecycle leaves them alone.
- Bad: a plan or ADR can no longer link to the code it is about; it names the file in plain text,
  which a reader cannot click.
- Bad: an edit adding such a link is refused and has to be made again.

## Out of scope

- A file path written as plain text, such as in backticks, which is not a link.
- Links a document already held before the edit, which stay until someone removes them.
- A link to a heading of the same document, or a web link starting `//`.
- Which lifecycle documents may refer to which, left to the agents that review each document.
- Edits not made with the agent's file-editing tools.

## How we'll check

Applies to: any edit an agent makes to one of the five kinds of lifecycle document.

1. Test: unit tests give the hook edits to each kind that add links to code, a folder, another
   `docs/` file and a lifecycle document, and check that only the last passes.
2. Test: a sample conversation asks for a spec linking to another page under `docs/`, and the spec
   written states what it needs in its own words instead.

## Open questions

- None.

## Technical detail

**The hook.** `scripts/reference_check.py` runs just before each Write, Edit or MultiEdit, as
[ADR 0026](0026-outside-material-references.md) set out, and reads the same kinds of link. An edit
is refused if it adds a target that:

- is an address of a kind other than `http`, `https` or `mailto`, such as `file:`;
- starts at the root of the computer or at a home folder (`~`);
- leads outside the repository;
- leads to anything in the repository, file or folder, that is not the brief, a spec, an ADR, a
  plan or a spike record.

The check that an ADR's link to another ADR names a file that exists is unchanged.

**The refusal's reason.** The message says the document links only to other lifecycle documents and
to the web, because anything else can change or vanish without the document being edited, and asks
the agent to state what matters in the document's own words or to name a file as plain text.

**Wording elsewhere.** The rules the lifecycle page and each reviewer's checklist hold for
references say the same, and no longer say that `docs/` holds only the lifecycle's documents or that
links to code are outside the rule.

[^lifecycle]: The lifecycle's documents are the five kinds its skills write: the brief (what the product is and who it is for), specs (what one capability should do), ADRs, plans (one piece of work to build) and spike records (the write-up of a throwaway experiment that tests one idea).
[^hook]: A hook is a script the coding tool runs automatically at set moments, here just before the agent edits a file.
