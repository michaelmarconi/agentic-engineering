# Software Development Lifecycle (SDLC) plugin for Claude Code

A plugin, an add-on, for Claude Code, Anthropic's artificial intelligence (AI) coding assistant, that has Claude take
software work from an idea to reviewed code on the main branch along one defined path, keeping
the reasoning in a few short documents.

## Problem

People who build software with an AI coding assistant decide what to build, and how, in
conversation with it. Those conversations end, and what was decided, and why, ends with them.
Each person directs the assistant in their own way, so nothing checks that the code still does
what was intended, or follows what was decided.

The maintainer, Michael Marconi, met this in an earlier set of instructions of his own for
Claude Code. Its instructions grew past a 500-line budget each, and mixed step-by-step
procedure with policy and notes about past incidents, until they were hard to follow or change.

## Who it's for

- Michael Marconi: the maintainer, and for now the only user, who builds this plugin and uses it
  in his own projects.
- People outside the project who install it: none yet. Version 1.0 is released when the first
  one does.

## Goals

- None stated yet; see Open questions.

## Out of scope

- Releasing software. How a project releases differs too much from one project to the next to
  follow one path.

## Constraints

- It must work when installed in any repository without changing anything there, apart from the
  documents it writes for the lifecycle: the product's brief, its specs, its decision records and
  its plans.
- It runs inside Claude Code, and only there.

## Open questions

- How often does Michael meet this problem?
- Who are the first outside users meant to be?
- What should change, measurably, for someone who uses the plugin?
- How would that change be observed or counted?
