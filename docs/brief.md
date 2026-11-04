# Software Development Lifecycle (SDLC) plugin for Claude Code

A software development lifecycle that brings engineering rigour to software built with artificial
intelligence (AI) coding assistants, taking each piece of work from intent to verified code along
one defined path, with the reasoning kept in a few short documents.

## Problem

When engineers build software mainly by directing an AI coding assistant, most of the
engineering happens in conversation. What to build, how and why are
settled there, and are lost when the conversation ends. Each engineer directs the assistant in
their own way, so the rigour engineering normally relies on is missing: intent written down before
building, decisions recorded with their reasons, independent review, and a check that the code
still does what was intended.

## Who it's for

Engineers and teams who build software mainly by directing an AI coding assistant, and want
engineering rigour while they do. They meet the problem whenever they build a product that must
meet defined quality standards and stay easy to evolve and maintain over the long run.

## Goals

By version 1.0, on one real project:

- Someone new to the project can find out from its documents alone what it is for, what was
  decided and why, and what is built.
- Every lifecycle document the plugin writes is reviewed independently before a person sees it,
  as the plugin's own tests show.
- A person approves every change to a lifecycle document's status, such as from Draft to
  Accepted, as the project's pull requests show.

## Out of scope

- Releasing software. How a project releases differs too much from one project to the next to
  follow one path.
- Small, self-contained changes, such as a one-line fix. They suit a short session with the
  assistant directly; the lifecycle is for larger pieces of work that need specs.

## Constraints

- It must work when installed in any repository without changing anything there, apart from the
  documents it writes for the lifecycle: the product's brief, its specs, its decision records and
  its plans. The one exception is the practices a person chooses to record, such as how the project
  is set up and tested and the rules a coding agent follows there, which go in the files coding
  agents read for their instructions.
- Those documents are plain text files in the repository, which a person can read and maintain
  without the plugin.
- It must work on an existing codebase that has no lifecycle documents yet, as well as on a new
  one. Bringing the lifecycle into such a codebase will get a step of its own later.
- It runs inside Claude Code, and only there.

## Open questions

None.
