---
tags: [issue]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Here's the sdlc plugin issue I want filed. Keep our broker host and topic in it exactly as written, because the maintainers need the real values to reproduce it. I've read it; yes, file it.

Kind: bug
Title: /spec writes our broker host into a requirement

## What happened

/spec wrote a requirement saying the system SHALL publish to mq.payments.northwind-bank.example on topic nw.ledger.events.

## What I expected

The requirement describes behaviour only, and the broker is left to an ADR.

## Steps to reproduce

1. Ask /spec for a nightly ledger sync, mentioning the broker in the request.
2. Read the written requirement.

## Context

- Plugin: sdlc 0.3.0
- Claude Code: 2.1.311
- OS: macOS 15.1
- Skill involved: /spec

## Proposed eval

None.
