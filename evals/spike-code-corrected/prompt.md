---
tags: [spike, known-flaky]
# Flaky: the agent sometimes changes the code before a run shows the fault, or reruns after
# an edit fails; 1 of 9 runs passed on 2026-11-19 and 2026-11-20.
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent, Bash]
---

Run the spike in docs/spikes/2026-11-02-quoted-field-with-line-break.md.
