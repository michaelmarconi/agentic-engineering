---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Here's our conversation about where to keep login sessions, pasted from earlier:

> **Me:** Sessions live in each web server's memory, so people get logged out whenever the load balancer sends them to another server or we deploy.
> **You:** Options: Postgres, Redis, or signed cookies holding the whole session.
> **Me:** Cookies are out: we need to be able to end a session from the server when we lock an account.
> **Me:** Let's go with Postgres, every server already talks to it.
> **You:** Session reads would then be one more query on every request.
> **Me:** Hmm, at our traffic that's a lot. Actually let's use Redis instead; we already run it for caching, and Postgres would add a query to every request.
> **Me:** We'll check it in code review: session data only goes through Redis.
> **Me:** The downside is that if Redis loses its data, everyone has to log in again.

Please record this decision as docs/adrs/0001-store-sessions-in-redis.md.
