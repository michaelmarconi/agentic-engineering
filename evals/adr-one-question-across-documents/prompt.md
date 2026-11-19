---
tags: [adr]
max_turns: 90
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Write two ADRs for our small web app. One chooses a search library: we're weighing Postgres full-text search against Meilisearch and haven't decided. The other chooses how the app checks who is calling its API: API keys or OAuth tokens, also undecided. Put them in docs/adrs/ as 0001-search-library.md and 0002-api-caller-checks.md, then take me through whatever needs deciding.
