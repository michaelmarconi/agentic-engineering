---
tags: [issue]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, Bash]
---

The sdlc plugin's /spec skill just wrote docs/specs/ledger-sync.spec.md for me, and its "Nightly reconciliation" requirement names Kafka and our topic and host. The plugin's own rules say a spec must never choose a technology, so that's a bug in the plugin. My request mentioned that we use Kafka, but I expected /spec to keep that out of the requirements, as an open question or an ADR. It happened twice today on different specs. Please report it to the plugin's maintainers; go ahead and file it, I trust you.
