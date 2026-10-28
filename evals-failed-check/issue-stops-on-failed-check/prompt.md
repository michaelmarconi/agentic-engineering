---
tags: [issue]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Here's an sdlc plugin bug I want filed. Tidy it up so it passes your review.

Kind: bug
Title: /spec asks all its questions at once

## What happened

After drafting a spec, /spec listed all five of its open questions in one reply instead of asking them one at a time.

## Steps to reproduce

1. Ask /spec for a spec about exporting invoices, giving few details.
2. Read its first reply after the draft.

## Context

- Plugin: sdlc 0.6.0
- Skill involved: /spec

## Proposed eval

A case that gives /spec a thin request and checks the reply asks one question.
